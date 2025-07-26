from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Schema for sending a chat message."""

    message: str = Field(..., min_length=1, max_length=2000)
    farm_id: Optional[int] = None
    language: str = Field(default="kn", pattern="^(kn|en)$")
    is_voice_message: bool = False
    audio_duration: Optional[float] = Field(None, ge=0)


class ChatResponse(BaseModel):
    """Schema for chat response."""

    id: int
    user_id: int
    farm_id: Optional[int]
    user_message: str
    ai_response: str
    message_type: str
    intent: Optional[str]
    language: str
    context_data: Optional[dict]
    is_voice_message: bool
    audio_duration: Optional[float]
    actions_triggered: Optional[List[Any]]
    follow_up_needed: bool
    user_rating: Optional[int]
    user_feedback: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
