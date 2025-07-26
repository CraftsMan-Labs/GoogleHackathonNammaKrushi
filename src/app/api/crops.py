from __future__ import annotations

import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..models.crop import Crop
from ..models.user import User
from ..schemas.crop import CropCreate, CropResponse, CropUpdate
from ..utils.auth import get_current_user

router = APIRouter(prefix="/crops", tags=["crops"])


def generate_crop_code(user_id: int, crop_name: str) -> str:
    """Generate a unique crop code."""
    # Simple crop code generation: first 3 letters of name + user_id + random
    name_part = "".join(c.upper() for c in crop_name if c.isalpha())[:3]
    return f"{name_part}{user_id}{str(uuid.uuid4())[:4].upper()}"


@router.post("/", response_model=CropResponse, status_code=status.HTTP_201_CREATED)
def create_crop(
    crop_data: CropCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Crop:
    """Create a new crop."""
    # Generate unique crop code
    crop_code = generate_crop_code(current_user.id, crop_data.crop_name)

    # Create crop
    db_crop = Crop(
        user_id=current_user.id, crop_code=crop_code, **crop_data.model_dump()
    )

    db.add(db_crop)
    db.commit()
    db.refresh(db_crop)

    return db_crop


@router.get("/", response_model=List[CropResponse])
def get_user_crops(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> List[Crop]:
    """Get all crops for the current user."""
    return db.query(Crop).filter(Crop.user_id == current_user.id).all()


@router.get("/{crop_id}", response_model=CropResponse)
def get_crop(
    crop_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Crop:
    """Get a specific crop by ID."""
    crop = (
        db.query(Crop)
        .filter(Crop.id == crop_id, Crop.user_id == current_user.id)
        .first()
    )

    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found"
        )

    return crop


@router.put("/{crop_id}", response_model=CropResponse)
def update_crop(
    crop_id: int,
    crop_update: CropUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Crop:
    """Update a crop."""
    crop = (
        db.query(Crop)
        .filter(Crop.id == crop_id, Crop.user_id == current_user.id)
        .first()
    )

    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found"
        )

    # Update crop with provided data
    update_data = crop_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(crop, field, value)

    db.commit()
    db.refresh(crop)

    return crop


@router.delete("/{crop_id}")
def delete_crop(
    crop_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    """Delete a crop."""
    crop = (
        db.query(Crop)
        .filter(Crop.id == crop_id, Crop.user_id == current_user.id)
        .first()
    )

    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found"
        )

    db.delete(crop)
    db.commit()

    return {"message": "Crop deleted successfully"}