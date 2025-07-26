from __future__ import annotations

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON,
    Boolean,
    Float,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..config.database import Base


class ChatHistory(Base):
    """Chat history with AI assistant."""

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    farm_id = Column(
        Integer, ForeignKey("farms.id"), nullable=True
    )  # if farm-specific query

    # Message Content
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)

    # Message Classification
    message_type = Column(
        String, default="general"
    )  # general, farm_specific, weather, sales, disease, market
    intent = Column(String)  # question, request, complaint, compliment
    language = Column(String, default="kn")  # kn (Kannada), en (English)

    # Context and Metadata
    context_data = Column(JSON)  # Additional context used for response
    confidence_score = Column(Float)  # AI confidence in response

    # Voice Interaction
    is_voice_message = Column(Boolean, default=False)
    audio_duration = Column(Float)  # in seconds
    voice_transcript_confidence = Column(Float)

    # Response Actions
    actions_triggered = Column(
        JSON
    )  # List of actions taken (create_todo, send_alert, etc.)
    follow_up_needed = Column(Boolean, default=False)

    # User Feedback
    user_rating = Column(Integer)  # 1-5 rating
    user_feedback = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="chat_history")
