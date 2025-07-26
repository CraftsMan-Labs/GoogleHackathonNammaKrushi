from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..config.database import Base


class CropRecommendation(Base):
    """AI-generated crop recommendations for farmers."""
    
    __tablename__ = "crop_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Recommendation Details
    recommended_crop = Column(String)
    recommended_variety = Column(String)
    current_crop = Column(String)
    season = Column(String)  # kharif, rabi, summer
    
    # Analysis Basis
    reason = Column(Text)
    analysis_factors = Column(JSON)  # soil, weather, market, historical data
    confidence_score = Column(Float)  # 0-100
    
    # Economic Projections
    expected_profit_increase = Column(Float)
    estimated_yield_per_acre = Column(Float)
    estimated_cost_per_acre = Column(Float)
    estimated_revenue_per_acre = Column(Float)
    break_even_price = Column(Float)
    
    # Market Analysis
    seasonal_suitability = Column(String)  # excellent, good, fair, poor
    market_demand = Column(String)  # high, medium, low
    price_trend = Column(String)  # increasing, stable, decreasing
    competition_level = Column(String)  # low, medium, high
    
    # Agricultural Factors
    soil_suitability = Column(String)  # excellent, good, fair, poor
    water_requirement = Column(String)  # low, medium, high
    climate_suitability = Column(String)  # excellent, good, fair, poor
    pest_disease_risk = Column(String)  # low, medium, high
    
    # Implementation
    planting_window_start = Column(String)
    planting_window_end = Column(String)
    harvest_timeline = Column(String)
    special_requirements = Column(Text)
    
    # Status
    status = Column(String, default="pending")  # pending, accepted, rejected, implemented
    farmer_feedback = Column(Text)
    implementation_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="crop_recommendations")