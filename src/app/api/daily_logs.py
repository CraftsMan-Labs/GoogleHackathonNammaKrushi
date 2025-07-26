from __future__ import annotations

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..models.daily_log import DailyLog
from ..models.crop import Crop
from ..models.user import User
from ..schemas.daily_log import DailyLogCreate, DailyLogResponse, DailyLogUpdate
from ..utils.auth import get_current_user

router = APIRouter(prefix="/daily-logs", tags=["daily-logs"])


def verify_crop_ownership(crop_id: int, user_id: int, db: Session) -> Crop:
    """Verify that the user owns the crop."""
    crop = db.query(Crop).filter(Crop.id == crop_id, Crop.user_id == user_id).first()

    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found"
        )

    return crop


@router.post(
    "/crops/{crop_id}/logs",
    response_model=DailyLogResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_daily_log(
    crop_id: int,
    log_data: DailyLogCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DailyLog:
    """Create a new daily log entry for a crop."""
    # Verify crop ownership
    verify_crop_ownership(crop_id, current_user.id, db)

    # Create daily log
    db_log = DailyLog(crop_id=crop_id, **log_data.model_dump())

    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    return db_log


@router.get("/crops/{crop_id}/logs", response_model=List[DailyLogResponse])
def get_crop_daily_logs(
    crop_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
) -> List[DailyLog]:
    """Get all daily logs for a crop."""
    # Verify crop ownership
    verify_crop_ownership(crop_id, current_user.id, db)

    return (
        db.query(DailyLog)
        .filter(DailyLog.crop_id == crop_id)
        .order_by(DailyLog.log_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/logs/{log_id}", response_model=DailyLogResponse)
def get_daily_log(
    log_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DailyLog:
    """Get a specific daily log entry."""
    log = (
        db.query(DailyLog)
        .join(Crop)
        .filter(DailyLog.id == log_id, Crop.user_id == current_user.id)
        .first()
    )

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Daily log not found"
        )

    return log


@router.put("/logs/{log_id}", response_model=DailyLogResponse)
def update_daily_log(
    log_id: int,
    log_update: DailyLogUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DailyLog:
    """Update a daily log entry."""
    log = (
        db.query(DailyLog)
        .join(Crop)
        .filter(DailyLog.id == log_id, Crop.user_id == current_user.id)
        .first()
    )

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Daily log not found"
        )

    # Update log with provided data
    update_data = log_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(log, field, value)

    db.commit()
    db.refresh(log)

    return log


@router.delete("/logs/{log_id}")
def delete_daily_log(
    log_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    """Delete a daily log entry."""
    log = (
        db.query(DailyLog)
        .join(Crop)
        .filter(DailyLog.id == log_id, Crop.user_id == current_user.id)
        .first()
    )

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Daily log not found"
        )

    db.delete(log)
    db.commit()

    return {"message": "Daily log deleted successfully"}


@router.get("/", response_model=List[DailyLogResponse])
def get_user_daily_logs(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
) -> List[DailyLog]:
    """Get all daily logs for the current user across all crops."""
    return (
        db.query(DailyLog)
        .join(Crop)
        .filter(Crop.user_id == current_user.id)
        .order_by(DailyLog.log_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )