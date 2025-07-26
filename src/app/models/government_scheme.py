from __future__ import annotations

from sqlalchemy import Column, Integer, String, Text, Date, Boolean, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy import DateTime

from ..config.database import Base


class GovernmentScheme(Base):
    """Government schemes and subsidies for farmers."""
    
    __tablename__ = "government_schemes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Scheme Details
    scheme_name = Column(String, nullable=False)
    scheme_code = Column(String, unique=True, index=True)
    description = Column(Text)
    detailed_description = Column(Text)
    
    # Eligibility
    eligibility_criteria = Column(Text)
    min_land_size_acres = Column(Float)
    max_land_size_acres = Column(Float)
    income_criteria = Column(String)
    age_criteria = Column(String)
    
    # Benefits
    benefit_amount = Column(String)
    benefit_type = Column(String)  # subsidy, loan, grant, insurance
    benefit_percentage = Column(Float)  # percentage of subsidy
    max_benefit_amount = Column(Float)
    
    # Application Details
    application_link = Column(String)
    application_process = Column(Text)
    required_documents = Column(JSON)  # List of required documents
    application_fee = Column(Float, default=0.0)
    
    # Scope and Applicability
    crop_types = Column(JSON)  # List of applicable crops
    location_applicable = Column(JSON)  # List of states/districts
    target_beneficiaries = Column(String)  # small_farmers, marginal_farmers, all
    
    # Timeline
    application_start_date = Column(Date)
    application_deadline = Column(Date)
    scheme_duration = Column(String)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_central_scheme = Column(Boolean, default=True)  # Central vs State scheme
    implementing_agency = Column(String)
    
    # Contact Information
    helpline_number = Column(String)
    contact_email = Column(String)
    office_address = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())