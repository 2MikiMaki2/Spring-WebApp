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

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                mode TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                conversation_id INTEGER NOT NULL REFERENCES conversations(id),
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)


async def close_db():
    global db_pool
    if db_pool:
        await db_pool.close()


# --- Helpers ---

def build_system_prompt(language: str, custom_prompt: str) -> str:
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


class SaveConversationRequest(BaseModel):
    mode: str
    messages: list[Message]


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


# --- Preferences ---

@app.get("/api/preferences")
async def get_preferences(user=Depends(get_current_user)):
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
    if request.target_language and request.target_language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail="Unsupported language")
    if request.voice and request.voice not in SUPPORTED_VOICES:
        raise HTTPException(status_code=400, detail="Unsupported voice")

    async with db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO preferences (user_id) VALUES ($1) "
            "ON CONFLICT (user_id) DO NOTHING",
            user["id"],
        )

        updates = {}
        if request.target_language is not None:
            updates["target_language"] = request.target_language
        if request.voice is not None:
            updates["voice"] = request.voice
        if request.custom_prompt is not None:
            updates["custom_prompt"] = request.custom_prompt

        if updates:
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


# --- Conversations ---

@app.post("/api/conversations")
async def save_conversation(
    request: SaveConversationRequest, user=Depends(get_current_user)
):
    """Save a completed conversation (text or voice) with all its messages."""

    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages to save")

    async with db_pool.acquire() as conn:
        # Create the conversation record.
        conv = await conn.fetchrow(
            "INSERT INTO conversations (user_id, mode) "
            "VALUES ($1, $2) RETURNING *",
            user["id"], request.mode,
        )

        # Insert all messages in one batch.
        await conn.executemany(
            "INSERT INTO messages (conversation_id, role, content) "
            "VALUES ($1, $2, $3)",
            [(conv["id"], m.role, m.content) for m in request.messages],
        )

    return {"conversation_id": conv["id"]}


@app.get("/api/conversations")
async def list_conversations(user=Depends(get_current_user)):
    """List all conversations for the current user, newest first."""

    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT c.id, c.mode, c.created_at, "
            "(SELECT content FROM messages WHERE conversation_id = c.id "
            " ORDER BY id LIMIT 1) AS first_message "
            "FROM conversations c "
            "WHERE c.user_id = $1 "
            "ORDER BY c.created_at DESC",
            user["id"],
        )

    return {
        "conversations": [
            {
                "id": row["id"],
                "mode": row["mode"],
                "created_at": row["created_at"].isoformat(),
                # Use the first message as a preview, truncated.
                "preview": (row["first_message"] or "")[:80],
            }
            for row in rows
        ],
    }


@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: int, user=Depends(get_current_user)):
    """Get the full transcript of a single conversation."""

    async with db_pool.acquire() as conn:
        conv = await conn.fetchrow(
            "SELECT * FROM conversations "
            "WHERE id = $1 AND user_id = $2",
            conversation_id, user["id"],
        )

        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

        msgs = await conn.fetch(
            "SELECT role, content, created_at FROM messages "
            "WHERE conversation_id = $1 ORDER BY id",
            conversation_id,
        )

    return {
        "conversation": {
            "id": conv["id"],
            "mode": conv["mode"],
            "created_at": conv["created_at"].isoformat(),
            "messages": [
                {
                    "role": row["role"],
                    "content": row["content"],
                    "created_at": row["created_at"].isoformat(),
                }
                for row in msgs
            ],
        },
    }


# --- Voice & Chat ---

@app.post("/api/token")
async def create_realtime_token(user=Depends(get_current_user)):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

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
                    "input_audio_transcription": {
                        "model": "whisper-1",
                    },
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