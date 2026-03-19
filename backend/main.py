import os
from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager
from typing import Optional

import asyncpg
import httpx
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from jose import jwt, JWTError

# --- Configuration ---

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
JWT_SECRET = os.environ.get("JWT_SECRET")
DATABASE_URL = os.environ.get("DATABASE_URL")

#TODO: Hardcoded options for languages and voices. Is there ability to fetch from OpenAI in real time?
SUPPORTED_LANGUAGES = [
    "English", "French", "Serbian", "Spanish", "German", "Italian",
    "Portuguese", "Japanese", "Korean", "Mandarin Chinese",
]

SUPPORTED_VOICES = [
    "alloy", "ash", "ballad", "coral", "echo",
    "sage", "shimmer", "verse", "marin", "cedar",
]

# --- Database ---

db_pool = None


async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)

    async with db_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                google_id TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                user_id INTEGER PRIMARY KEY REFERENCES users(id),
                target_language TEXT NOT NULL DEFAULT 'French',
                voice TEXT NOT NULL DEFAULT 'coral',
                custom_prompt TEXT NOT NULL DEFAULT ''
            )
        """)


async def close_db():
    global db_pool
    if db_pool:
        await db_pool.close()


# --- Helpers ---

def build_system_prompt(language: str, custom_prompt: str) -> str:
    """Build a system prompt from the user's preferences."""
    base = (
        f"You are a {language} conversation partner. "
        f"Speak in {language}. "
        f"Gently correct the user's mistakes. "
        f"Keep your responses concise and conversational."
    )
    if custom_prompt.strip():
        base += f"\n\nAdditional context: {custom_prompt.strip()}"
    return base


async def get_user_preferences(user_id: int):
    """Fetch preferences for a user, or return defaults if none exist."""
    async with db_pool.acquire() as conn:
        prefs = await conn.fetchrow(
            "SELECT * FROM preferences WHERE user_id = $1", user_id
        )
    if prefs:
        return dict(prefs)
    return {
        "user_id": user_id,
        "target_language": "French",
        "voice": "coral",
        "custom_prompt": "",
    }


# --- App lifecycle ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Auth helpers ---

security = HTTPBearer()


def create_jwt(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        payload = jwt.decode(
            credentials.credentials, JWT_SECRET, algorithms=["HS256"]
        )
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    async with db_pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# --- Request/response schemas ---

class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class GoogleAuthRequest(BaseModel):
    credential: str


class PreferencesUpdate(BaseModel):
    target_language: Optional[str] = None
    voice: Optional[str] = None
    custom_prompt: Optional[str] = None


# --- Endpoints ---

@app.get("/health")
def health_check():
    return {"status": "ok", "phase": 5}


@app.get("/api/auth/config")
def auth_config():
    return {"google_client_id": GOOGLE_CLIENT_ID}


@app.post("/api/auth/google")
async def auth_google(request: GoogleAuthRequest):
    try:
        id_info = id_token.verify_oauth2_token(
            request.credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    google_id = id_info["sub"]
    email = id_info.get("email", "")
    name = id_info.get("name", "")

    async with db_pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE google_id = $1", google_id
        )

        if not user:
            user = await conn.fetchrow(
                "INSERT INTO users (google_id, email, name) "
                "VALUES ($1, $2, $3) RETURNING *",
                google_id, email, name,
            )
            # Create default preferences for the new user.
            await conn.execute(
                "INSERT INTO preferences (user_id) VALUES ($1)",
                user["id"],
            )

    token = create_jwt(user["id"])
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
        },
    }


@app.get("/api/preferences")
async def get_preferences(user=Depends(get_current_user)):
    """Return the current user's preferences and the available options."""
    prefs = await get_user_preferences(user["id"])
    return {
        "preferences": {
            "target_language": prefs["target_language"],
            "voice": prefs["voice"],
            "custom_prompt": prefs["custom_prompt"],
        },
        "options": {
            "languages": SUPPORTED_LANGUAGES,
            "voices": SUPPORTED_VOICES,
        },
    }


@app.put("/api/preferences")
async def update_preferences(
    request: PreferencesUpdate, user=Depends(get_current_user)
):
    """Update the current user's preferences."""

    # Validate inputs if provided.
    if request.target_language and request.target_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail="Unsupported language")
    if request.voice and request.voice not in SUPPORTED_VOICES:
        raise HTTPException(status_code=400, detail="Unsupported voice")

    async with db_pool.acquire() as conn:
        # Ensure a preferences row exists (handles users created before
        # this feature was added).
        await conn.execute(
            "INSERT INTO preferences (user_id) VALUES ($1) "
            "ON CONFLICT (user_id) DO NOTHING",
            user["id"],
        )

        # Build the update dynamically based on which fields were sent.
        updates = {}
        if request.target_language is not None:
            updates["target_language"] = request.target_language
        if request.voice is not None:
            updates["voice"] = request.voice
        if request.custom_prompt is not None:
            updates["custom_prompt"] = request.custom_prompt

        if updates:
            # Build a SET clause like: target_language = $2, voice = $3
            set_parts = []
            values = [user["id"]]
            for i, (key, val) in enumerate(updates.items(), start=2):
                set_parts.append(f"{key} = ${i}")
                values.append(val)

            query = (
                f"UPDATE preferences SET {', '.join(set_parts)} "
                f"WHERE user_id = $1"
            )
            await conn.execute(query, *values)

    prefs = await get_user_preferences(user["id"])
    return {
        "preferences": {
            "target_language": prefs["target_language"],
            "voice": prefs["voice"],
            "custom_prompt": prefs["custom_prompt"],
        },
    }


@app.post("/api/token")
async def create_realtime_token(user=Depends(get_current_user)):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    # Use the user's preferences to configure the session.
    prefs = await get_user_preferences(user["id"])
    prompt = build_system_prompt(prefs["target_language"], prefs["custom_prompt"])

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/realtime/client_secrets",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "session": {
                    "type": "realtime",
                    "model": "gpt-realtime",
                    "instructions": prompt,
                    "audio": {
                        "output": {
                            "voice": prefs["voice"],
                        }
                    },
                }
            },
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Failed to generate token from OpenAI",
        )

    return response.json()


@app.post("/api/chat")
async def chat(request: ChatRequest, user=Depends(get_current_user)):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    # Use the user's preferences to build the system prompt.
    prefs = await get_user_preferences(user["id"])
    prompt = build_system_prompt(prefs["target_language"], prefs["custom_prompt"])

    messages = [
        {"role": "system", "content": prompt},
        *[m.model_dump() for m in request.messages],
    ]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "messages": messages,
            },
            timeout=30.0,
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Failed to get response from OpenAI",
        )

    data = response.json()
    reply = data["choices"][0]["message"]["content"]
    return {"reply": reply}