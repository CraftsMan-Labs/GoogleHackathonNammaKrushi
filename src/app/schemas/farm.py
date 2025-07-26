from __future__ import annotations

from datetime import datetime, date
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class FarmCreate(BaseModel):
    """Schema for creating a new farm."""

    farm_name: str = Field(..., min_length=2, max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = Field(None, max_length=500)
    village: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=50)
    state: str = Field(default="Karnataka", max_length=50)
    total_area_acres: Optional[float] = Field(None, gt=0)
    cultivable_area_acres: Optional[float] = Field(None, gt=0)
    soil_type: Optional[str] = Field(None, max_length=50)
    water_source: Optional[str] = Field(None, max_length=100)
    irrigation_type: Optional[str] = Field(None, max_length=50)
    current_crop: Optional[str] = Field(None, max_length=50)
    crop_variety: Optional[str] = Field(None, max_length=50)
    planting_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    crop_stage: str = Field(default="seedling", max_length=50)


class FarmUpdate(BaseModel):
    """Schema for updating farm information."""

    farm_name: Optional[str] = Field(None, min_length=2, max_length=100)
    address: Optional[str] = Field(None, max_length=500)
    village: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=50)
    total_area_acres: Optional[float] = Field(None, gt=0)
    cultivable_area_acres: Optional[float] = Field(None, gt=0)
    soil_type: Optional[str] = Field(None, max_length=50)
    water_source: Optional[str] = Field(None, max_length=100)
    irrigation_type: Optional[str] = Field(None, max_length=50)
    current_crop: Optional[str] = Field(None, max_length=50)
    crop_variety: Optional[str] = Field(None, max_length=50)
    planting_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    crop_stage: Optional[str] = Field(None, max_length=50)
    crop_health_score: Optional[float] = Field(None, ge=0, le=100)


class FarmResponse(BaseModel):
    """Schema for farm response."""

    id: int
    user_id: int
    farm_name: str
    farm_code: Optional[str]
    latitude: float
    longitude: float
    address: Optional[str]
    village: Optional[str]
    district: Optional[str]
    state: str
    total_area_acres: Optional[float]
    cultivable_area_acres: Optional[float]
    soil_type: Optional[str]
    water_source: Optional[str]
    irrigation_type: Optional[str]
    current_crop: Optional[str]
    crop_variety: Optional[str]
    planting_date: Optional[date]
    expected_harvest_date: Optional[date]
    crop_stage: str
    crop_health_score: float
    previous_crops: Optional[List[Any]]
    average_yield: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
