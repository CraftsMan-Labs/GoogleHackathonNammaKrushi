from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Schema for sending a chat message."""

    message: str = Field(..., min_length=1, max_length=2000)
    crop_id: Optional[int] = None
    language: str = Field(default="kn", pattern="^(kn|en)$")
    is_voice_message: bool = False  # Always False, kept for backward compatibility


class ChatResponse(BaseModel):
    """Schema for chat response."""

    id: int
    user_id: int
    crop_id: Optional[int]
    user_message: str
    ai_response: str
    message_type: str
    intent: Optional[str]
    language: str
    context_data: Optional[dict]
    is_voice_message: bool  # Always False, kept for backward compatibility
    actions_triggered: Optional[List[Any]]
    follow_up_needed: bool
    user_rating: Optional[int]
    user_feedback: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
