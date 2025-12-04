from typing import List, Optional

from pydantic import BaseModel, Field


class ChatTurn(BaseModel):
    role: str = Field(..., description="Speaker role such as 'user' or 'assistant'.")
    content: str = Field(..., description="Message content for the given role.")
    timestamp: str = Field(..., description="ISO-8601 timestamp representing when the message was logged.")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Latest user utterance.")
    session_id: Optional[str] = Field(
        default=None, description="Existing session identifier to preserve history."
    )


class ChatResponse(BaseModel):
    reply: str = Field(..., description="Bot reply for the supplied message.")
    session_id: str = Field(..., description="Session identifier associated with the chat.")
    history: List[ChatTurn] = Field(
        default_factory=list,
        description="Chronological conversation turns including the latest exchange.",
    )
