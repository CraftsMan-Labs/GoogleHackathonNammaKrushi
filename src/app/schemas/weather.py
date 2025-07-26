from __future__ import annotations

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class WeatherCreate(BaseModel):
    """Schema for creating weather data."""
    weather_date: date = Field(default_factory=lambda: date.today())
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    location_name: Optional[str] = Field(None, max_length=100)
    temperature: Optional[float] = Field(None, ge=-50, le=60)
    feels_like: Optional[float] = Field(None, ge=-50, le=60)
    humidity: Optional[float] = Field(None, ge=0, le=100)
    pressure: Optional[float] = Field(None, ge=0)
    visibility: Optional[float] = Field(None, ge=0)
    uv_index: Optional[float] = Field(None, ge=0, le=15)
    rainfall: Optional[float] = Field(None, ge=0)
    rainfall_probability: Optional[float] = Field(None, ge=0, le=100)
    wind_speed: Optional[float] = Field(None, ge=0)
    wind_direction: Optional[str] = Field(None, max_length=10)
    wind_gust: Optional[float] = Field(None, ge=0)
    conditions: Optional[str] = Field(None, max_length=50)
    weather_description: Optional[str] = Field(None, max_length=200)
    is_forecast: bool = False
    forecast_days_ahead: int = Field(default=0, ge=0, le=7)
    alerts: Optional[str] = Field(None, max_length=1000)
    recommended_actions: Optional[str] = Field(None, max_length=1000)
    crop_impact_assessment: Optional[str] = Field(None, max_length=500)
    irrigation_recommendation: Optional[str] = Field(None, max_length=200)
    pest_disease_risk: Optional[str] = Field(None, pattern="^(low|medium|high)$")


class WeatherResponse(BaseModel):
    """Schema for weather response."""
    id: int
    user_id: int
    weather_date: date
    latitude: Optional[float]
    longitude: Optional[float]
    location_name: Optional[str]
    temperature: Optional[float]
    feels_like: Optional[float]
    humidity: Optional[float]
    pressure: Optional[float]
    visibility: Optional[float]
    uv_index: Optional[float]
    rainfall: Optional[float]
    rainfall_probability: Optional[float]
    wind_speed: Optional[float]
    wind_direction: Optional[str]
    wind_gust: Optional[float]
    conditions: Optional[str]
    weather_description: Optional[str]
    is_forecast: bool
    forecast_days_ahead: int
    alerts: Optional[str]
    recommended_actions: Optional[str]
    crop_impact_assessment: Optional[str]
    irrigation_recommendation: Optional[str]
    pest_disease_risk: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True