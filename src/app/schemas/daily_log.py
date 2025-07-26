from __future__ import annotations

from datetime import datetime, date
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class DailyLogCreate(BaseModel):
    """Schema for creating a daily log entry."""

    log_date: date = Field(default_factory=lambda: date.today())
    activity_type: Optional[str] = Field(None, max_length=50)
    activity_details: Optional[dict] = None
    notes: Optional[str] = Field(None, max_length=1000)
    voice_transcript: Optional[str] = Field(None, max_length=2000)
    crop_health_observation: Optional[str] = Field(None, max_length=50)
    crop_health_notes: Optional[str] = Field(None, max_length=500)
    diseases_noted: Optional[str] = Field(None, max_length=500)
    pest_spotted: bool = False
    disease_spotted: bool = False
    weather_temp: Optional[float] = Field(None, ge=-50, le=60)
    weather_humidity: Optional[float] = Field(None, ge=0, le=100)
    weather_rainfall: Optional[float] = Field(None, ge=0)
    weather_conditions: Optional[str] = Field(None, max_length=100)
    images: Optional[List[str]] = None


class DailyLogUpdate(BaseModel):
    """Schema for updating a daily log entry."""

    activity_type: Optional[str] = Field(None, max_length=50)
    activity_details: Optional[dict] = None
    notes: Optional[str] = Field(None, max_length=1000)
    voice_transcript: Optional[str] = Field(None, max_length=2000)
    crop_health_observation: Optional[str] = Field(None, max_length=50)
    crop_health_notes: Optional[str] = Field(None, max_length=500)
    diseases_noted: Optional[str] = Field(None, max_length=500)
    pest_spotted: Optional[bool] = None
    disease_spotted: Optional[bool] = None
    weather_temp: Optional[float] = Field(None, ge=-50, le=60)
    weather_humidity: Optional[float] = Field(None, ge=0, le=100)
    weather_rainfall: Optional[float] = Field(None, ge=0)
    weather_conditions: Optional[str] = Field(None, max_length=100)
    ai_insights: Optional[str] = Field(None, max_length=1000)


class DailyLogResponse(BaseModel):
    """Schema for daily log response."""

    id: int
    farm_id: int
    log_date: date
    activity_type: Optional[str]
    activity_details: Optional[dict]
    notes: Optional[str]
    voice_note_url: Optional[str]
    voice_transcript: Optional[str]
    crop_health_observation: Optional[str]
    crop_health_notes: Optional[str]
    diseases_noted: Optional[str]
    pest_spotted: bool
    disease_spotted: bool
    weather_temp: Optional[float]
    weather_humidity: Optional[float]
    weather_rainfall: Optional[float]
    weather_conditions: Optional[str]
    images: Optional[List[str]]
    video_path: Optional[str]
    ai_insights: Optional[str]
    ai_recommendations: Optional[List[Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
