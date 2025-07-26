from __future__ import annotations

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..models.daily_log import DailyLog
from ..models.farm import Farm
from ..models.user import User
from ..schemas.daily_log import DailyLogCreate, DailyLogResponse, DailyLogUpdate
from ..utils.auth import get_current_user

router = APIRouter(prefix="/daily-logs", tags=["daily-logs"])


def verify_farm_ownership(farm_id: int, user_id: int, db: Session) -> Farm:
    """Verify that the user owns the farm."""
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.user_id == user_id).first()

    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Farm not found"
        )

    return farm


@router.post(
    "/farms/{farm_id}/logs",
    response_model=DailyLogResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_daily_log(
    farm_id: int,
    log_data: DailyLogCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> DailyLog:
    """Create a new daily log entry for a farm."""
    # Verify farm ownership
    verify_farm_ownership(farm_id, current_user.id, db)

    # Create daily log
    db_log = DailyLog(farm_id=farm_id, **log_data.model_dump())

    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    return db_log


@router.get("/farms/{farm_id}/logs", response_model=List[DailyLogResponse])
def get_farm_daily_logs(
    farm_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
) -> List[DailyLog]:
    """Get all daily logs for a farm."""
    # Verify farm ownership
    verify_farm_ownership(farm_id, current_user.id, db)

    return (
        db.query(DailyLog)
        .filter(DailyLog.farm_id == farm_id)
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
        .join(Farm)
        .filter(DailyLog.id == log_id, Farm.user_id == current_user.id)
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
        .join(Farm)
        .filter(DailyLog.id == log_id, Farm.user_id == current_user.id)
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
        .join(Farm)
        .filter(DailyLog.id == log_id, Farm.user_id == current_user.id)
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
    """Get all daily logs for the current user across all farms."""
    return (
        db.query(DailyLog)
        .join(Farm)
        .filter(Farm.user_id == current_user.id)
        .order_by(DailyLog.log_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
