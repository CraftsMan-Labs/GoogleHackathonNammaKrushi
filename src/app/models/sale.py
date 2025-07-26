from __future__ import annotations

from datetime import date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..config.database import Base


class Sale(Base):
    """Sales tracking for farm produce."""
    
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    
    # Sale Details
    sale_date = Column(Date, nullable=False, default=date.today)
    crop_type = Column(String)
    crop_variety = Column(String)
    quantity_kg = Column(Float)
    price_per_kg = Column(Float)
    total_amount = Column(Float)
    
    # Buyer Information
    buyer_name = Column(String)
    buyer_type = Column(String)  # direct, market, middleman, export, online
    buyer_contact = Column(String)
    
    # Transaction Details
    payment_method = Column(String)  # cash, bank_transfer, cheque, upi
    payment_status = Column(String, default="pending")  # pending, completed, partial
    transportation_cost = Column(Float)
    commission_paid = Column(Float)
    
    # Quality & Grading
    quality_grade = Column(String)  # A, B, C grade
    quality_notes = Column(Text)
    
    # Market Information
    market_location = Column(String)
    market_price_reference = Column(Float)  # Reference market price
    
    # Additional Details
    notes = Column(Text)
    invoice_number = Column(String)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    farm = relationship("Farm", back_populates="sales")