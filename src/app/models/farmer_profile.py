from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
    JSON,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..config.database import Base


class FarmerProfile(Base):
    """Comprehensive farmer profile model for detailed agricultural information."""

    __tablename__ = "farmer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    # Basic Farmer Information
    farmer_name = Column(String, nullable=False)  # Full name of the farmer
    preferred_language = Column(
        String, default="english"
    )  # english, hindi, kannada, tamil, etc.

    # Land Information
    total_land_size_acres = Column(Float)  # Total land owned/operated
    cultivable_land_acres = Column(Float)  # Land suitable for cultivation
    crop_covered_area_acres = Column(Float)  # Currently under crops

    # Land Ownership/Tenure
    land_ownership_type = Column(
        String
    )  # owned, leased, rented, sharecropping, family_land
    ownership_documents = Column(
        JSON
    )  # List of document types: ["title_deed", "lease_agreement", etc.]
    lease_duration_years = Column(Float)  # If leased/rented
    rental_amount_per_acre = Column(Float)  # Annual rent per acre

    # Previous Crop History (Last 3 years)
    previous_crops_year1 = Column(
        JSON
    )  # [{"crop": "rice", "area": 2.5, "yield": 1200, "season": "kharif"}]
    previous_crops_year2 = Column(JSON)
    previous_crops_year3 = Column(JSON)

    # Current Farming Practices
    primary_crops = Column(JSON)  # Main crops currently grown
    secondary_crops = Column(JSON)  # Secondary/rotation crops
    cropping_pattern = Column(
        String
    )  # monocropping, intercropping, mixed_cropping, crop_rotation

    # Irrigation Information
    irrigation_method = Column(String)  # drip, sprinkler, flood, furrow, rainfed
    water_source = Column(JSON)  # ["borewell", "canal", "river", "pond", "rainwater"]
    irrigation_area_coverage = Column(Float)  # Percentage of land with irrigation
    water_availability = Column(String)  # abundant, adequate, scarce, seasonal

    # Fertilizer Usage
    fertilizers_used = Column(
        JSON
    )  # [{"type": "urea", "quantity_per_acre": 50, "frequency": "seasonal"}]
    organic_fertilizers = Column(JSON)  # Organic fertilizers used
    fertilizer_application_method = Column(
        String
    )  # broadcasting, placement, foliar, fertigation
    annual_fertilizer_cost = Column(Float)  # Total annual cost

    # Pest and Disease Management
    pest_problems_faced = Column(JSON)  # Common pests encountered
    disease_problems_faced = Column(JSON)  # Common diseases
    pesticides_used = Column(JSON)  # Pesticides/fungicides used
    pest_control_methods = Column(
        JSON
    )  # ["chemical", "organic", "biological", "integrated"]

    # Previous Treatments and Interventions
    soil_treatments_done = Column(JSON)  # Previous soil treatments
    land_preparation_methods = Column(JSON)  # Plowing, harrowing, etc.
    seed_treatment_practices = Column(JSON)  # Seed treatments used
    post_harvest_practices = Column(JSON)  # Storage, processing methods

    # Technology and Equipment
    farm_equipment_owned = Column(JSON)  # Equipment owned
    technology_adoption = Column(JSON)  # Digital tools, sensors, etc.
    mechanization_level = Column(String)  # high, medium, low, manual

    # Economic Information
    annual_farm_income = Column(Float)  # Approximate annual income
    major_expenses = Column(JSON)  # Major cost categories
    market_access = Column(String)  # direct, through_middleman, cooperative, online
    storage_facilities = Column(JSON)  # Available storage options

    # Challenges and Support
    major_challenges = Column(JSON)  # Main farming challenges
    government_schemes_availed = Column(JSON)  # Government programs used
    training_programs_attended = Column(JSON)  # Agricultural training received
    extension_services_used = Column(JSON)  # Extension services accessed

    # Goals and Aspirations
    farming_goals = Column(JSON)  # Short and long-term goals
    crops_interested_to_try = Column(JSON)  # New crops to experiment with
    technology_interest = Column(JSON)  # Technologies interested in adopting

    # Profile Completion Status
    profile_completion_percentage = Column(Float, default=0.0)
    is_profile_complete = Column(Boolean, default=False)
    last_updated_section = Column(String)  # Track which section was last updated

    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="farmer_profile")

    def calculate_completion_percentage(self) -> float:
        """Calculate profile completion percentage based on filled fields."""
        total_sections = 12  # Number of major sections
        completed_sections = 0

        # Basic Information (required)
        if self.farmer_name and self.preferred_language:
            completed_sections += 1

        # Land Information
        if self.total_land_size_acres and self.land_ownership_type:
            completed_sections += 1

        # Crop History
        if self.previous_crops_year1 or self.primary_crops:
            completed_sections += 1

        # Irrigation
        if self.irrigation_method and self.water_source:
            completed_sections += 1

        # Fertilizers
        if self.fertilizers_used:
            completed_sections += 1

        # Pest Management
        if self.pest_control_methods:
            completed_sections += 1

        # Previous Treatments
        if self.soil_treatments_done or self.land_preparation_methods:
            completed_sections += 1

        # Technology
        if self.farm_equipment_owned or self.mechanization_level:
            completed_sections += 1

        # Economic
        if self.market_access:
            completed_sections += 1

        # Challenges
        if self.major_challenges:
            completed_sections += 1

        # Support
        if self.government_schemes_availed or self.training_programs_attended:
            completed_sections += 1

        # Goals
        if self.farming_goals:
            completed_sections += 1

        percentage = (completed_sections / total_sections) * 100
        self.profile_completion_percentage = percentage
        self.is_profile_complete = percentage >= 80.0

        return percentage

    def get_farming_experience_summary(self) -> dict:
        """Generate a summary of farming experience."""
        summary = {
            "total_land": self.total_land_size_acres or 0,
            "years_of_data": 0,
            "unique_crops_grown": set(),
            "primary_irrigation": self.irrigation_method,
            "land_ownership": self.land_ownership_type,
        }

        # Analyze crop history
        for year_data in [
            self.previous_crops_year1,
            self.previous_crops_year2,
            self.previous_crops_year3,
        ]:
            if year_data:
                summary["years_of_data"] += 1
                for crop_info in year_data:
                    if isinstance(crop_info, dict) and "crop" in crop_info:
                        summary["unique_crops_grown"].add(crop_info["crop"])

        # Add current crops
        if self.primary_crops:
            for crop in self.primary_crops:
                if isinstance(crop, str):
                    summary["unique_crops_grown"].add(crop)
                elif isinstance(crop, dict) and "name" in crop:
                    summary["unique_crops_grown"].add(crop["name"])

        summary["unique_crops_grown"] = list(summary["unique_crops_grown"])
        summary["total_unique_crops"] = len(summary["unique_crops_grown"])

        return summary
