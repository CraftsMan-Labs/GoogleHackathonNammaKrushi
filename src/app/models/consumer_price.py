from __future__ import annotations

from datetime import date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text
from sqlalchemy.sql import func

from ..config.database import Base


class ConsumerPrice(Base):
    """Consumer price tracking for market analysis and supply chain optimization."""

    __tablename__ = "consumer_prices"

    id = Column(Integer, primary_key=True, index=True)

    # Price Details
    price_date = Column(Date, nullable=False, default=date.today)
    crop_type = Column(String, nullable=False)
    crop_variety = Column(String)
    price_per_kg = Column(Float, nullable=False)
    
    # Market Information
    market_location = Column(String, nullable=False)
    market_type = Column(String)  # wholesale, retail, supermarket, online, local_market
    vendor_name = Column(String)
    vendor_type = Column(String)  # retailer, wholesaler, supermarket, online_platform
    
    # Quality & Grading
    quality_grade = Column(String)  # A, B, C grade
    quality_notes = Column(Text)
    
    # Supply Chain Information
    source_region = Column(String)  # Where the produce originated
    transportation_distance_km = Column(Float)
    supply_chain_stages = Column(String)  # farmer->wholesaler->retailer, direct, etc.
    
    # Market Conditions
    availability_status = Column(String)  # abundant, normal, scarce, out_of_stock
    demand_level = Column(String)  # high, medium, low
    seasonal_factor = Column(String)  # peak_season, off_season, normal
    
    # Price Analysis
    price_trend = Column(String)  # increasing, decreasing, stable
    price_volatility = Column(String)  # high, medium, low
    competitor_price_min = Column(Float)
    competitor_price_max = Column(Float)
    
    # Additional Details
    notes = Column(Text)
    data_source = Column(String)  # manual_entry, api_import, market_survey
    verified = Column(String, default="pending")  # verified, pending, disputed
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())