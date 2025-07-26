from __future__ import annotations

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class ConsumerPriceCreate(BaseModel):
    """Schema for creating a consumer price record."""

    price_date: date = Field(default_factory=lambda: date.today())
    crop_type: str = Field(..., max_length=50)
    crop_variety: Optional[str] = Field(None, max_length=50)
    price_per_kg: float = Field(..., gt=0)
    market_location: str = Field(..., max_length=100)
    market_type: Optional[str] = Field(None, max_length=50)
    vendor_name: Optional[str] = Field(None, max_length=100)
    vendor_type: Optional[str] = Field(None, max_length=50)
    quality_grade: Optional[str] = Field(None, max_length=10)
    quality_notes: Optional[str] = Field(None, max_length=500)
    source_region: Optional[str] = Field(None, max_length=100)
    transportation_distance_km: Optional[float] = Field(None, ge=0)
    supply_chain_stages: Optional[str] = Field(None, max_length=200)
    availability_status: Optional[str] = Field(None, max_length=50)
    demand_level: Optional[str] = Field(None, max_length=20)
    seasonal_factor: Optional[str] = Field(None, max_length=30)
    price_trend: Optional[str] = Field(None, max_length=20)
    price_volatility: Optional[str] = Field(None, max_length=20)
    competitor_price_min: Optional[float] = Field(None, ge=0)
    competitor_price_max: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=500)
    data_source: Optional[str] = Field(None, max_length=50)
    verified: str = Field(default="pending", pattern="^(verified|pending|disputed)$")


class ConsumerPriceUpdate(BaseModel):
    """Schema for updating a consumer price record."""

    crop_type: Optional[str] = Field(None, max_length=50)
    crop_variety: Optional[str] = Field(None, max_length=50)
    price_per_kg: Optional[float] = Field(None, gt=0)
    market_location: Optional[str] = Field(None, max_length=100)
    market_type: Optional[str] = Field(None, max_length=50)
    vendor_name: Optional[str] = Field(None, max_length=100)
    vendor_type: Optional[str] = Field(None, max_length=50)
    quality_grade: Optional[str] = Field(None, max_length=10)
    quality_notes: Optional[str] = Field(None, max_length=500)
    source_region: Optional[str] = Field(None, max_length=100)
    transportation_distance_km: Optional[float] = Field(None, ge=0)
    supply_chain_stages: Optional[str] = Field(None, max_length=200)
    availability_status: Optional[str] = Field(None, max_length=50)
    demand_level: Optional[str] = Field(None, max_length=20)
    seasonal_factor: Optional[str] = Field(None, max_length=30)
    price_trend: Optional[str] = Field(None, max_length=20)
    price_volatility: Optional[str] = Field(None, max_length=20)
    competitor_price_min: Optional[float] = Field(None, ge=0)
    competitor_price_max: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=500)
    data_source: Optional[str] = Field(None, max_length=50)
    verified: Optional[str] = Field(None, pattern="^(verified|pending|disputed)$")


class ConsumerPriceResponse(BaseModel):
    """Schema for consumer price response."""

    id: int
    price_date: date
    crop_type: str
    crop_variety: Optional[str]
    price_per_kg: float
    market_location: str
    market_type: Optional[str]
    vendor_name: Optional[str]
    vendor_type: Optional[str]
    quality_grade: Optional[str]
    quality_notes: Optional[str]
    source_region: Optional[str]
    transportation_distance_km: Optional[float]
    supply_chain_stages: Optional[str]
    availability_status: Optional[str]
    demand_level: Optional[str]
    seasonal_factor: Optional[str]
    price_trend: Optional[str]
    price_volatility: Optional[str]
    competitor_price_min: Optional[float]
    competitor_price_max: Optional[float]
    notes: Optional[str]
    data_source: Optional[str]
    verified: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True