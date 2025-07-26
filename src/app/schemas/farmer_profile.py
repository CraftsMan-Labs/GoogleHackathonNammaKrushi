from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CropHistory(BaseModel):
    """Schema for individual crop history entry."""

    crop: str = Field(..., description="Crop name")
    area: float = Field(..., description="Area in acres")
    yield_per_acre: Optional[float] = Field(None, description="Yield per acre")
    season: Optional[str] = Field(None, description="Growing season")
    year: Optional[int] = Field(None, description="Year grown")


class FertilizerUsage(BaseModel):
    """Schema for fertilizer usage information."""

    type: str = Field(..., description="Fertilizer type")
    quantity_per_acre: float = Field(..., description="Quantity used per acre")
    frequency: str = Field(..., description="Application frequency")
    cost_per_application: Optional[float] = Field(
        None, description="Cost per application"
    )


class FarmerProfileCreate(BaseModel):
    """Schema for creating farmer profile."""

    # Basic Information
    farmer_name: str = Field(..., min_length=2, max_length=100)
    preferred_language: str = Field(
        default="english", description="Preferred language for app"
    )

    # Land Information
    total_land_size_acres: Optional[float] = Field(
        None, ge=0, description="Total land size in acres"
    )
    cultivable_land_acres: Optional[float] = Field(
        None, ge=0, description="Cultivable land in acres"
    )
    crop_covered_area_acres: Optional[float] = Field(
        None, ge=0, description="Area under crops"
    )

    # Land Ownership
    land_ownership_type: Optional[str] = Field(
        None, description="Type of land ownership"
    )
    ownership_documents: Optional[List[str]] = Field(
        None, description="Ownership documents"
    )
    lease_duration_years: Optional[float] = Field(
        None, ge=0, description="Lease duration if applicable"
    )
    rental_amount_per_acre: Optional[float] = Field(
        None, ge=0, description="Rental amount per acre"
    )

    # Crop History
    previous_crops_year1: Optional[List[CropHistory]] = Field(
        None, description="Crops grown in previous year"
    )
    previous_crops_year2: Optional[List[CropHistory]] = Field(
        None, description="Crops grown 2 years ago"
    )
    previous_crops_year3: Optional[List[CropHistory]] = Field(
        None, description="Crops grown 3 years ago"
    )

    # Current Farming
    primary_crops: Optional[List[str]] = Field(
        None, description="Primary crops currently grown"
    )
    secondary_crops: Optional[List[str]] = Field(None, description="Secondary crops")
    cropping_pattern: Optional[str] = Field(None, description="Cropping pattern used")

    # Irrigation
    irrigation_method: Optional[str] = Field(
        None, description="Primary irrigation method"
    )
    water_source: Optional[List[str]] = Field(
        None, description="Water sources available"
    )
    irrigation_area_coverage: Optional[float] = Field(
        None, ge=0, le=100, description="% of land with irrigation"
    )
    water_availability: Optional[str] = Field(
        None, description="Water availability status"
    )

    # Fertilizers
    fertilizers_used: Optional[List[FertilizerUsage]] = Field(
        None, description="Fertilizers used"
    )
    organic_fertilizers: Optional[List[str]] = Field(
        None, description="Organic fertilizers used"
    )
    fertilizer_application_method: Optional[str] = Field(
        None, description="Application method"
    )
    annual_fertilizer_cost: Optional[float] = Field(
        None, ge=0, description="Annual fertilizer cost"
    )

    # Pest Management
    pest_problems_faced: Optional[List[str]] = Field(
        None, description="Common pest problems"
    )
    disease_problems_faced: Optional[List[str]] = Field(
        None, description="Common diseases"
    )
    pesticides_used: Optional[List[str]] = Field(None, description="Pesticides used")
    pest_control_methods: Optional[List[str]] = Field(
        None, description="Pest control methods"
    )

    # Previous Treatments
    soil_treatments_done: Optional[List[str]] = Field(
        None, description="Previous soil treatments"
    )
    land_preparation_methods: Optional[List[str]] = Field(
        None, description="Land preparation methods"
    )
    seed_treatment_practices: Optional[List[str]] = Field(
        None, description="Seed treatment practices"
    )
    post_harvest_practices: Optional[List[str]] = Field(
        None, description="Post-harvest practices"
    )


class FarmerProfileUpdate(BaseModel):
    """Schema for updating farmer profile (all fields optional)."""

    farmer_name: Optional[str] = Field(None, min_length=2, max_length=100)
    preferred_language: Optional[str] = None
    total_land_size_acres: Optional[float] = Field(None, ge=0)
    cultivable_land_acres: Optional[float] = Field(None, ge=0)
    crop_covered_area_acres: Optional[float] = Field(None, ge=0)
    land_ownership_type: Optional[str] = None
    ownership_documents: Optional[List[str]] = None
    lease_duration_years: Optional[float] = Field(None, ge=0)
    rental_amount_per_acre: Optional[float] = Field(None, ge=0)
    previous_crops_year1: Optional[List[CropHistory]] = None
    previous_crops_year2: Optional[List[CropHistory]] = None
    previous_crops_year3: Optional[List[CropHistory]] = None
    primary_crops: Optional[List[str]] = None
    secondary_crops: Optional[List[str]] = None
    cropping_pattern: Optional[str] = None
    irrigation_method: Optional[str] = None
    water_source: Optional[List[str]] = None
    irrigation_area_coverage: Optional[float] = Field(None, ge=0, le=100)
    water_availability: Optional[str] = None
    fertilizers_used: Optional[List[FertilizerUsage]] = None
    organic_fertilizers: Optional[List[str]] = None
    fertilizer_application_method: Optional[str] = None
    annual_fertilizer_cost: Optional[float] = Field(None, ge=0)
    pest_problems_faced: Optional[List[str]] = None
    disease_problems_faced: Optional[List[str]] = None
    pesticides_used: Optional[List[str]] = None
    pest_control_methods: Optional[List[str]] = None
    soil_treatments_done: Optional[List[str]] = None
    land_preparation_methods: Optional[List[str]] = None
    seed_treatment_practices: Optional[List[str]] = None
    post_harvest_practices: Optional[List[str]] = None


class FarmerProfileResponse(BaseModel):
    """Schema for farmer profile response."""

    id: int
    user_id: int
    farmer_name: str
    preferred_language: str

    # Land Information
    total_land_size_acres: Optional[float]
    cultivable_land_acres: Optional[float]
    crop_covered_area_acres: Optional[float]
    land_ownership_type: Optional[str]

    # Current Farming
    primary_crops: Optional[List[str]]
    irrigation_method: Optional[str]

    # Profile Status
    profile_completion_percentage: float
    is_profile_complete: bool
    last_updated_section: Optional[str]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FarmerProfileDetailed(FarmerProfileResponse):
    """Detailed farmer profile response with all fields."""

    ownership_documents: Optional[List[str]]
    lease_duration_years: Optional[float]
    rental_amount_per_acre: Optional[float]
    previous_crops_year1: Optional[List[Dict[str, Any]]]
    previous_crops_year2: Optional[List[Dict[str, Any]]]
    previous_crops_year3: Optional[List[Dict[str, Any]]]
    secondary_crops: Optional[List[str]]
    cropping_pattern: Optional[str]
    water_source: Optional[List[str]]
    irrigation_area_coverage: Optional[float]
    water_availability: Optional[str]
    fertilizers_used: Optional[List[Dict[str, Any]]]
    organic_fertilizers: Optional[List[str]]
    fertilizer_application_method: Optional[str]
    annual_fertilizer_cost: Optional[float]
    pest_problems_faced: Optional[List[str]]
    disease_problems_faced: Optional[List[str]]
    pesticides_used: Optional[List[str]]
    pest_control_methods: Optional[List[str]]
    soil_treatments_done: Optional[List[str]]
    land_preparation_methods: Optional[List[str]]
    seed_treatment_practices: Optional[List[str]]
    post_harvest_practices: Optional[List[str]]


class ProfileSection(BaseModel):
    """Schema for updating specific profile sections."""

    section_name: str = Field(..., description="Name of the section being updated")
    section_data: Dict[str, Any] = Field(..., description="Section data")


class FarmingExperienceSummary(BaseModel):
    """Schema for farming experience summary."""

    total_land: float
    years_of_data: int
    unique_crops_grown: List[str]
    total_unique_crops: int
    primary_irrigation: Optional[str]
    land_ownership: Optional[str]
