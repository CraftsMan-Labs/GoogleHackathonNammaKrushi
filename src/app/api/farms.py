from __future__ import annotations

import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..models.farm import Farm
from ..models.user import User
from ..schemas.farm import FarmCreate, FarmResponse, FarmUpdate
from ..utils.auth import get_current_user

router = APIRouter(prefix="/farms", tags=["farms"])


def generate_farm_code(user_id: int, farm_name: str) -> str:
    """Generate a unique farm code."""
    # Simple farm code generation: first 3 letters of name + user_id + random
    name_part = ''.join(c.upper() for c in farm_name if c.isalpha())[:3]
    return f"{name_part}{user_id}{str(uuid.uuid4())[:4].upper()}"


@router.post("/", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
def create_farm(
    farm_data: FarmCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
) -> Farm:
    """Create a new farm."""
    # Generate unique farm code
    farm_code = generate_farm_code(current_user.id, farm_data.farm_name)
    
    # Create farm
    db_farm = Farm(
        user_id=current_user.id,
        farm_code=farm_code,
        **farm_data.model_dump()
    )
    
    db.add(db_farm)
    db.commit()
    db.refresh(db_farm)
    
    return db_farm


@router.get("/", response_model=List[FarmResponse])
def get_user_farms(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
) -> List[Farm]:
    """Get all farms for the current user."""
    return db.query(Farm).filter(Farm.user_id == current_user.id).all()


@router.get("/{farm_id}", response_model=FarmResponse)
def get_farm(
    farm_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
) -> Farm:
    """Get a specific farm by ID."""
    farm = db.query(Farm).filter(
        Farm.id == farm_id,
        Farm.user_id == current_user.id
    ).first()
    
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    return farm


@router.put("/{farm_id}", response_model=FarmResponse)
def update_farm(
    farm_id: int,
    farm_update: FarmUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
) -> Farm:
    """Update a farm."""
    farm = db.query(Farm).filter(
        Farm.id == farm_id,
        Farm.user_id == current_user.id
    ).first()
    
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    # Update farm with provided data
    update_data = farm_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(farm, field, value)
    
    db.commit()
    db.refresh(farm)
    
    return farm


@router.delete("/{farm_id}")
def delete_farm(
    farm_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
) -> dict[str, str]:
    """Delete a farm."""
    farm = db.query(Farm).filter(
        Farm.id == farm_id,
        Farm.user_id == current_user.id
    ).first()
    
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    db.delete(farm)
    db.commit()
    
    return {"message": "Farm deleted successfully"}