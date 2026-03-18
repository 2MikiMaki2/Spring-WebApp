import os

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Read API key once at startup from Railway's environment variables.
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# CORS: allow the frontend (on a different Railway domain) to call this backend.
# Using ["*"] permits any origin — fine for development, but we should
# restrict this to our frontend's URL before going to production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "phase": 2}


@app.post("/api/token")
async def create_token():
    """Request an ephemeral token from OpenAI for the Realtime API."""

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
                    "instructions": (
                        "You are a French conversation partner. "
                        "Speak in French. "
                        "Gently correct the user's mistakes. "
                        "Keep your responses concise and conversational."
                    ),
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