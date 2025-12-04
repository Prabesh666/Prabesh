import logging
import os
from datetime import datetime, timezone
from typing import Dict, List
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from chatbot import get_ai_response
from .schemas import ChatRequest, ChatResponse, ChatTurn

# Configure logging once for the service
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("codeit-chatbot")

# Preload environment secrets
load_dotenv()

app = FastAPI(title="CodeIT Chatbot API", version="1.0.0")

# Allow frontend origin override via env, defaulting to permissive for local dev
# Normalize CORS configuration from environment
raw_origins = [origin.strip() for origin in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",") if origin.strip()]
if not raw_origins:
    raw_origins = ["*"]

allow_credentials_env = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"
allow_credentials = allow_credentials_env and "*" not in raw_origins
if allow_credentials_env and not allow_credentials:
    logger.warning("Disabling credentialed CORS because wildcard origins are in use.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=raw_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory store keyed by session identifier
SessionHistory = List[Dict[str, str]]
sessions: Dict[str, SessionHistory] = {}


@app.on_event("startup")
def startup_event() -> None:
    """Eagerly import heavy resources on process start."""
    try:
        # Trigger a lightweight call to ensure embeddings and dataset are loaded.
        _ = get_ai_response("Hello")
        logger.info("Chatbot backend warmed up successfully.")
    except Exception as exc:  # pragma: no cover - diagnostic logging only
        logger.exception("Chatbot warm-up failed: %s", exc)
        raise


@app.get("/health", tags=["system"])
def healthcheck() -> Dict[str, str]:
    """Expose application liveness for uptime checks."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse, tags=["chat"])
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Return a chatbot reply and updated history for a given session."""
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    session_id = request.session_id or str(uuid4())
    history = sessions.setdefault(session_id, [])

    # Convert history to list of dicts for chatbot
    chat_history = [{"role": turn["role"], "content": turn["content"]} for turn in history]

    try:
        reply = get_ai_response(message, history=chat_history)
    except Exception as exc:
        logger.exception("Chatbot response generation failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(exc)}")

    now = datetime.now(timezone.utc).isoformat()
    history.append({"role": "user", "content": message, "timestamp": now})
    history.append({"role": "assistant", "content": reply, "timestamp": datetime.now(timezone.utc).isoformat()})

    turns = [ChatTurn(**turn) for turn in history]
    return ChatResponse(reply=reply, session_id=session_id, history=turns)
