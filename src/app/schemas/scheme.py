"""
Government Scheme Schema Models

Pydantic models for government scheme search and structured output.
"""

from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field


class SchemeSearchRequest(BaseModel):
    """Request model for scheme search."""

    query: str = Field(
        ...,
        description="Search query for government schemes (e.g., 'agricultural subsidies for farmers in Karnataka')",
        min_length=3,
        max_length=500,
    )
    max_results: Optional[int] = Field(
        default=10, description="Maximum number of schemes to return", ge=1, le=20
    )


class GovernmentScheme(BaseModel):
    """Structured model for a government scheme."""

    title: str = Field(
        ...,
        description="Official title/name of the government scheme",
        min_length=5,
        max_length=200,
    )
    description: str = Field(
        ...,
        description="Detailed description of the scheme, its benefits, and eligibility",
        min_length=20,
        max_length=1000,
    )
    scheme_link: Optional[str] = Field(
        default=None, description="Official website URL or link to the scheme details"
    )
    department: Optional[str] = Field(
        default=None,
        description="Government department or ministry responsible for the scheme",
        max_length=100,
    )
    eligibility: Optional[str] = Field(
        default=None,
        description="Key eligibility criteria for the scheme",
        max_length=500,
    )
    benefits: Optional[str] = Field(
        default=None,
        description="Key benefits or financial assistance provided",
        max_length=500,
    )
    application_process: Optional[str] = Field(
        default=None, description="How to apply for the scheme", max_length=300
    )
    target_beneficiaries: Optional[str] = Field(
        default=None,
        description="Target group or beneficiaries (e.g., 'Small and marginal farmers')",
        max_length=200,
    )
    state_or_central: Optional[str] = Field(
        default=None,
        description="Whether it's a state or central government scheme",
        max_length=50,
    )


class SchemeSearchResponse(BaseModel):
    """Response model for scheme search results."""

    status: str = Field(..., description="Status of the search operation")
    query: str = Field(..., description="Original search query")
    total_schemes: int = Field(..., description="Total number of schemes found", ge=0)
    schemes: List[GovernmentScheme] = Field(
        ..., description="List of government schemes matching the search criteria"
    )
    search_metadata: Optional[dict] = Field(
        default=None, description="Additional metadata about the search operation"
    )


class SchemeSearchError(BaseModel):
    """Error response model for scheme search."""

    status: str = Field(default="error")
    error_message: str = Field(
        ..., description="Description of the error that occurred"
    )
    query: Optional[str] = Field(
        default=None, description="Original search query that caused the error"
    )
