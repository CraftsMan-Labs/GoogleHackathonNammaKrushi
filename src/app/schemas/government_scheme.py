from __future__ import annotations

from datetime import datetime, date
from typing import Optional, List, Any
from pydantic import BaseModel


class GovernmentSchemeResponse(BaseModel):
    """Schema for government scheme response."""
    id: int
    scheme_name: str
    scheme_code: Optional[str]
    description: Optional[str]
    detailed_description: Optional[str]
    eligibility_criteria: Optional[str]
    min_land_size_acres: Optional[float]
    max_land_size_acres: Optional[float]
    income_criteria: Optional[str]
    age_criteria: Optional[str]
    benefit_amount: Optional[str]
    benefit_type: Optional[str]
    benefit_percentage: Optional[float]
    max_benefit_amount: Optional[float]
    application_link: Optional[str]
    application_process: Optional[str]
    required_documents: Optional[List[Any]]
    application_fee: Optional[float]
    crop_types: Optional[List[Any]]
    location_applicable: Optional[List[Any]]
    target_beneficiaries: Optional[str]
    application_start_date: Optional[date]
    application_deadline: Optional[date]
    scheme_duration: Optional[str]
    is_active: bool
    is_central_scheme: bool
    implementing_agency: Optional[str]
    helpline_number: Optional[str]
    contact_email: Optional[str]
    office_address: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True