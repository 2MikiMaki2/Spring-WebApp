import os

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

SYSTEM_PROMPT = (
    "You are a French conversation partner. "
    "Speak in French. "
    "Gently correct the user's mistakes. "
    "Keep your responses concise and conversational."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Schema for the /api/chat request body.
# Pydantic validates the incoming JSON automatically —
# if the frontend sends the wrong shape, FastAPI returns a clear error.
class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


@app.get("/health")
def health_check():
    return {"status": "ok", "phase": 3}


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
async def chat(request: ChatRequest):
    """Send a text conversation to OpenAI and return the assistant's reply."""

    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    # Prepend the system prompt to the conversation history.
    # The frontend sends only user/assistant messages; the system
    # message is always added here so it can't be tampered with.
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