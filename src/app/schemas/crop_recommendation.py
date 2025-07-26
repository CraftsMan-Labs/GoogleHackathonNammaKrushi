from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel


class CropRecommendationResponse(BaseModel):
    """Schema for crop recommendation response."""
    id: int
    user_id: int
    recommended_crop: Optional[str]
    recommended_variety: Optional[str]
    current_crop: Optional[str]
    season: Optional[str]
    reason: Optional[str]
    analysis_factors: Optional[List[Any]]
    confidence_score: Optional[float]
    expected_profit_increase: Optional[float]
    estimated_yield_per_acre: Optional[float]
    estimated_cost_per_acre: Optional[float]
    estimated_revenue_per_acre: Optional[float]
    break_even_price: Optional[float]
    seasonal_suitability: Optional[str]
    market_demand: Optional[str]
    price_trend: Optional[str]
    competition_level: Optional[str]
    soil_suitability: Optional[str]
    water_requirement: Optional[str]
    climate_suitability: Optional[str]
    pest_disease_risk: Optional[str]
    planting_window_start: Optional[str]
    planting_window_end: Optional[str]
    harvest_timeline: Optional[str]
    special_requirements: Optional[str]
    status: str
    farmer_feedback: Optional[str]
    implementation_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True