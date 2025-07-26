from __future__ import annotations

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..config.database import Base


class User(Base):
    """User model for farmers."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    phone = Column(String)
    location = Column(String)
    district = Column(String)
    state = Column(String, default="Karnataka")
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    farms = relationship("Farm", back_populates="owner", cascade="all, delete-orphan")
    todos = relationship(
        "TodoTask", back_populates="user", cascade="all, delete-orphan"
    )
    weather_history = relationship(
        "WeatherHistory", back_populates="user", cascade="all, delete-orphan"
    )
    chat_history = relationship(
        "ChatHistory", back_populates="user", cascade="all, delete-orphan"
    )
