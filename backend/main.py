import os
from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager

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

SYSTEM_PROMPT = (
    "You are a French conversation partner. "
    "Speak in French. "
    "Gently correct the user's mistakes. "
    "Keep your responses concise and conversational."
)

# --- Database ---

# A "pool" is a set of reusable database connections. Instead of opening
# and closing a connection for every request (slow), the pool keeps
# several connections open and hands them out as needed.
db_pool = None


async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)

    # Create the users table if it doesn't exist yet.
    # SERIAL means the id auto-increments (1, 2, 3, ...).
    # google_id is the unique identifier Google assigns to each account.
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


async def close_db():
    global db_pool
    if db_pool:
        await db_pool.close()


# --- App lifecycle ---
# The lifespan context manager runs init_db when the app starts
# and close_db when it shuts down.

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

# HTTPBearer tells FastAPI to look for an "Authorization: Bearer <token>"
# header on requests that require authentication.
security = HTTPBearer()


def create_jwt(user_id: int) -> str:
    """Create a signed JWT that expires in 7 days."""
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Verify the JWT from the request header and return the user.

    This is a FastAPI "dependency" — any endpoint that includes
    user=Depends(get_current_user) in its parameters will automatically
    require a valid JWT. If the token is missing or invalid, FastAPI
    returns a 401 before the endpoint code even runs.
    """
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


# --- Endpoints ---

@app.get("/health")
def health_check():
    return {"status": "ok", "phase": 4}


@app.get("/api/auth/config")
def auth_config():
    """Return the Google Client ID so the frontend can initialize
    the sign-in button without hardcoding it."""
    return {"google_client_id": GOOGLE_CLIENT_ID}


@app.post("/api/auth/google")
async def auth_google(request: GoogleAuthRequest):
    """Verify a Google ID token, create or find the user, return a JWT."""

    # Verify the token is real and was issued by Google for our app.
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
        # Check if this Google account is already in our database.
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE google_id = $1", google_id
        )

        if not user:
            # First time signing in — create a new user.
            user = await conn.fetchrow(
                "INSERT INTO users (google_id, email, name) "
                "VALUES ($1, $2, $3) RETURNING *",
                google_id,
                email,
                name,
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


@app.post("/api/token")
async def create_realtime_token(user=Depends(get_current_user)):
    """Request an ephemeral token from OpenAI for the Realtime API.
    Requires authentication."""

    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

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
                    "instructions": SYSTEM_PROMPT,
                    "audio": {
                        "output": {
                            "voice": "coral",
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
    """Send a text conversation to OpenAI and return the assistant's reply.
    Requires authentication."""

    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
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