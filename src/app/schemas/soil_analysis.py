from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SoilAnalysisCreate(BaseModel):
    """Schema for creating a soil analysis."""

    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    location_name: Optional[str] = Field(
        None, max_length=200, description="Human-readable location name"
    )


class SoilAnalysisUpdate(BaseModel):
    """Schema for updating soil analysis."""

    location_name: Optional[str] = Field(None, max_length=200)
    recommendations: Optional[str] = None
    suitable_crops: Optional[List[str]] = None


class SoilAnalysisResponse(BaseModel):
    """Schema for soil analysis response."""

    id: int
    user_id: int
    latitude: float
    longitude: float
    location_name: Optional[str]

    # Analysis Results
    summary: Optional[str]

    # Key Properties
    ph_value: Optional[float]
    ph_description: Optional[str]
    organic_carbon: Optional[float]
    organic_carbon_description: Optional[str]
    clay_percentage: Optional[float]
    sand_percentage: Optional[float]
    silt_percentage: Optional[float]
    soil_texture: Optional[str]
    nitrogen_content: Optional[float]
    bulk_density: Optional[float]
    cation_exchange_capacity: Optional[float]

    # Quality and Recommendations
    soil_quality_score: Optional[float]
    recommendations: Optional[str]
    suitable_crops: Optional[List[str]]

    # Status and Metadata
    analysis_status: str
    analysis_date: datetime
    data_source: str
    created_at: datetime

    class Config:
        from_attributes = True


class SoilAnalysisDetailed(SoilAnalysisResponse):
    """Detailed soil analysis response including raw data."""

    raw_data: Optional[Dict[str, Any]]


class RegistrationProgress(BaseModel):
    """Schema for registration progress updates."""

    step: str = Field(..., description="Current step in registration")
    message: str = Field(..., description="Progress message")
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")


class RegistrationComplete(BaseModel):
    """Schema for completed registration response."""

    user_id: int
    message: str
    soil_analysis: Optional[SoilAnalysisResponse] = None
    recommendations: Optional[str] = None
    suitable_crops: Optional[List[str]] = None
