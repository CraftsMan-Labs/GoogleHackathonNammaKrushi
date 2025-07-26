"""
Farmer Profile API

Comprehensive farmer profile management for detailed agricultural information collection.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..models.user import User
from ..models.farmer_profile import FarmerProfile
from ..schemas.farmer_profile import (
    FarmerProfileCreate,
    FarmerProfileUpdate,
    FarmerProfileResponse,
    FarmerProfileDetailed,
    ProfileSection,
    FarmingExperienceSummary,
)
from ..utils.auth import get_current_user

router = APIRouter(prefix="/farmer-profile", tags=["farmer-profile"])


@router.post(
    "/", response_model=FarmerProfileResponse, status_code=status.HTTP_201_CREATED
)
def create_farmer_profile(
    profile_data: FarmerProfileCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> FarmerProfile:
    """Create a new farmer profile for the current user."""

    # Check if profile already exists
    existing_profile = (
        db.query(FarmerProfile).filter(FarmerProfile.user_id == current_user.id).first()
    )

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Farmer profile already exists. Use PUT to update.",
        )

    # Create new profile
    db_profile = FarmerProfile(
        user_id=current_user.id, **profile_data.model_dump(exclude_unset=True)
    )

    # Calculate completion percentage
    db_profile.calculate_completion_percentage()

    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)

    return db_profile


@router.get("/", response_model=FarmerProfileDetailed)
def get_farmer_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> FarmerProfile:
    """Get the current user's farmer profile."""

    profile = (
        db.query(FarmerProfile).filter(FarmerProfile.user_id == current_user.id).first()
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer profile not found. Please create a profile first.",
        )

    return profile


@router.put("/", response_model=FarmerProfileResponse)
def update_farmer_profile(
    profile_data: FarmerProfileUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> FarmerProfile:
    """Update the current user's farmer profile."""

    profile = (
        db.query(FarmerProfile).filter(FarmerProfile.user_id == current_user.id).first()
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer profile not found. Please create a profile first.",
        )

    # Update profile with provided data
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    # Recalculate completion percentage
    profile.calculate_completion_percentage()

    db.commit()
    db.refresh(profile)

    return profile


@router.patch("/section", response_model=FarmerProfileResponse)
def update_profile_section(
    section_update: ProfileSection,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> FarmerProfile:
    """Update a specific section of the farmer profile."""

    profile = (
        db.query(FarmerProfile).filter(FarmerProfile.user_id == current_user.id).first()
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer profile not found. Please create a profile first.",
        )

    # Update specific section
    for field, value in section_update.section_data.items():
        if hasattr(profile, field):
            setattr(profile, field, value)

    # Track last updated section
    profile.last_updated_section = section_update.section_name

    # Recalculate completion percentage
    profile.calculate_completion_percentage()

    db.commit()
    db.refresh(profile)

    return profile


@router.get("/summary", response_model=FarmingExperienceSummary)
def get_farming_experience_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """Get a summary of the farmer's experience and farming practices."""

    profile = (
        db.query(FarmerProfile).filter(FarmerProfile.user_id == current_user.id).first()
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Farmer profile not found."
        )

    return profile.get_farming_experience_summary()


@router.get("/completion-status")
def get_profile_completion_status(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """Get profile completion status and suggestions for improvement."""

    profile = (
        db.query(FarmerProfile).filter(FarmerProfile.user_id == current_user.id).first()
    )

    if not profile:
        return {
            "profile_exists": False,
            "completion_percentage": 0,
            "is_complete": False,
            "missing_sections": [
                "basic_information",
                "land_information",
                "crop_history",
                "irrigation",
                "fertilizers",
                "pest_management",
            ],
        }

    # Determine missing sections
    missing_sections = []

    if not profile.farmer_name:
        missing_sections.append("basic_information")
    if not profile.total_land_size_acres:
        missing_sections.append("land_information")
    if not profile.previous_crops_year1 and not profile.primary_crops:
        missing_sections.append("crop_history")
    if not profile.irrigation_method:
        missing_sections.append("irrigation")
    if not profile.fertilizers_used:
        missing_sections.append("fertilizers")
    if not profile.pest_control_methods:
        missing_sections.append("pest_management")

    return {
        "profile_exists": True,
        "completion_percentage": profile.profile_completion_percentage,
        "is_complete": profile.is_profile_complete,
        "missing_sections": missing_sections,
        "last_updated_section": profile.last_updated_section,
        "total_land": profile.total_land_size_acres,
        "primary_crops": profile.primary_crops,
        "irrigation_method": profile.irrigation_method,
    }


@router.delete("/")
def delete_farmer_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """Delete the current user's farmer profile."""

    profile = (
        db.query(FarmerProfile).filter(FarmerProfile.user_id == current_user.id).first()
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Farmer profile not found."
        )

    db.delete(profile)
    db.commit()

    return {"message": "Farmer profile deleted successfully"}
