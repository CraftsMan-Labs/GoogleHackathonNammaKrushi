from __future__ import annotations

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class SaleCreate(BaseModel):
    """Schema for creating a sale record."""
    sale_date: date = Field(default_factory=lambda: date.today())
    crop_type: Optional[str] = Field(None, max_length=50)
    crop_variety: Optional[str] = Field(None, max_length=50)
    quantity_kg: Optional[float] = Field(None, gt=0)
    price_per_kg: Optional[float] = Field(None, gt=0)
    total_amount: Optional[float] = Field(None, gt=0)
    buyer_name: Optional[str] = Field(None, max_length=100)
    buyer_type: Optional[str] = Field(None, max_length=50)
    buyer_contact: Optional[str] = Field(None, max_length=50)
    payment_method: Optional[str] = Field(None, max_length=50)
    payment_status: str = Field(default="pending", pattern="^(pending|completed|partial)$")
    transportation_cost: Optional[float] = Field(None, ge=0)
    commission_paid: Optional[float] = Field(None, ge=0)
    quality_grade: Optional[str] = Field(None, max_length=10)
    quality_notes: Optional[str] = Field(None, max_length=500)
    market_location: Optional[str] = Field(None, max_length=100)
    market_price_reference: Optional[float] = Field(None, gt=0)
    notes: Optional[str] = Field(None, max_length=500)
    invoice_number: Optional[str] = Field(None, max_length=50)


class SaleUpdate(BaseModel):
    """Schema for updating a sale record."""
    crop_type: Optional[str] = Field(None, max_length=50)
    crop_variety: Optional[str] = Field(None, max_length=50)
    quantity_kg: Optional[float] = Field(None, gt=0)
    price_per_kg: Optional[float] = Field(None, gt=0)
    total_amount: Optional[float] = Field(None, gt=0)
    buyer_name: Optional[str] = Field(None, max_length=100)
    buyer_type: Optional[str] = Field(None, max_length=50)
    buyer_contact: Optional[str] = Field(None, max_length=50)
    payment_method: Optional[str] = Field(None, max_length=50)
    payment_status: Optional[str] = Field(None, pattern="^(pending|completed|partial)$")
    transportation_cost: Optional[float] = Field(None, ge=0)
    commission_paid: Optional[float] = Field(None, ge=0)
    quality_grade: Optional[str] = Field(None, max_length=10)
    quality_notes: Optional[str] = Field(None, max_length=500)
    market_location: Optional[str] = Field(None, max_length=100)
    market_price_reference: Optional[float] = Field(None, gt=0)
    notes: Optional[str] = Field(None, max_length=500)
    invoice_number: Optional[str] = Field(None, max_length=50)


class SaleResponse(BaseModel):
    """Schema for sale response."""
    id: int
    farm_id: int
    sale_date: date
    crop_type: Optional[str]
    crop_variety: Optional[str]
    quantity_kg: Optional[float]
    price_per_kg: Optional[float]
    total_amount: Optional[float]
    buyer_name: Optional[str]
    buyer_type: Optional[str]
    buyer_contact: Optional[str]
    payment_method: Optional[str]
    payment_status: str
    transportation_cost: Optional[float]
    commission_paid: Optional[float]
    quality_grade: Optional[str]
    quality_notes: Optional[str]
    market_location: Optional[str]
    market_price_reference: Optional[float]
    notes: Optional[str]
    invoice_number: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True