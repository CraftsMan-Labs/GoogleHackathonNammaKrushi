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
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..config.database import Base


class WeatherHistory(Base):
    """Weather data and forecasts."""

    __tablename__ = "weather_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Date and Location
    date = Column(Date, nullable=False, default=date.today)
    latitude = Column(Float)
    longitude = Column(Float)
    location_name = Column(String)

    # Current Weather
    temperature = Column(Float)
    feels_like = Column(Float)
    humidity = Column(Float)
    pressure = Column(Float)
    visibility = Column(Float)
    uv_index = Column(Float)

    # Precipitation
    rainfall = Column(Float)
    rainfall_probability = Column(Float)

    # Wind
    wind_speed = Column(Float)
    wind_direction = Column(String)
    wind_gust = Column(Float)

    # General Conditions
    conditions = Column(String)  # sunny, cloudy, rainy, stormy
    weather_description = Column(String)

    # Forecast Data
    is_forecast = Column(Boolean, default=False)  # True for future predictions
    forecast_days_ahead = Column(Integer, default=0)

    # Alerts and Recommendations
    alerts = Column(Text)  # JSON array of weather alerts
    recommended_actions = Column(Text)  # AI-generated farming suggestions

    # Agricultural Impact
    crop_impact_assessment = Column(Text)
    irrigation_recommendation = Column(String)
    pest_disease_risk = Column(String)  # low, medium, high

    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="weather_history")
