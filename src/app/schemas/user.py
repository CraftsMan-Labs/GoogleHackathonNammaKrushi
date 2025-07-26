from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone: Optional[str] = Field(None, max_length=15)
    location: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=50)
    state: str = Field(default="Karnataka", max_length=50)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=15)
    location: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=50)
    state: Optional[str] = Field(None, max_length=50)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class UserResponse(BaseModel):
    """Schema for user response."""

    id: int
    name: str
    email: str
    phone: Optional[str]
    location: Optional[str]
    district: Optional[str]
    state: str
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str
