from __future__ import annotations

from datetime import date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Date,
    ForeignKey,
    Text,
    JSON,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..config.database import Base


class DailyLog(Base):
    """Daily farm activity logs."""

    __tablename__ = "daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)

    # Activity Details
    log_date = Column(Date, nullable=False, default=date.today)
    activity_type = Column(
        String
    )  # watering, fertilizing, pest_control, observation, harvesting
    activity_details = Column(JSON)
    notes = Column(Text)

    # Voice Journal
    voice_note_url = Column(String)
    voice_transcript = Column(Text)

    # Observations
    crop_health_observation = Column(String)
    crop_health_notes = Column(Text)
    diseases_noted = Column(Text)
    pest_spotted = Column(Boolean, default=False)
    disease_spotted = Column(Boolean, default=False)

    # Weather at time of log
    weather_temp = Column(Float)
    weather_humidity = Column(Float)
    weather_rainfall = Column(Float)
    weather_conditions = Column(String)

    # Media
    images = Column(JSON)  # List of image URLs
    video_path = Column(String)

    # AI Analysis
    ai_insights = Column(Text)
    ai_recommendations = Column(JSON)

    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    farm = relationship("Farm", back_populates="daily_logs")
