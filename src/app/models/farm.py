from __future__ import annotations

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Date,
    ForeignKey,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..config.database import Base


class Farm(Base):
    """Farm model for tracking farm details."""

    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    farm_name = Column(String, nullable=False)
    farm_code = Column(String, unique=True, index=True)

    # Location
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(Text)
    village = Column(String)
    district = Column(String)
    state = Column(String, default="Karnataka")

    # Farm Details
    total_area_acres = Column(Float)
    cultivable_area_acres = Column(Float)
    soil_type = Column(String)
    water_source = Column(String)
    irrigation_type = Column(String)

    # Current Crop
    current_crop = Column(String)
    crop_variety = Column(String)
    planting_date = Column(Date)
    expected_harvest_date = Column(Date)
    crop_stage = Column(
        String, default="seedling"
    )  # seedling, vegetative, flowering, fruiting, harvesting
    crop_health_score = Column(Float, default=100.0)  # 0-100

    # Historical Data
    previous_crops = Column(JSON)  # List of previous crops
    average_yield = Column(Float)

    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="farms")
    daily_logs = relationship(
        "DailyLog", back_populates="farm", cascade="all, delete-orphan"
    )
    todos = relationship(
        "TodoTask", back_populates="farm", cascade="all, delete-orphan"
    )
    sales = relationship("Sale", back_populates="farm", cascade="all, delete-orphan")
