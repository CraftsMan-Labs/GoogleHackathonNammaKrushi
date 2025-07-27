"""
Research Report Pydantic Schemas

Schemas for research report API requests and responses.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum


class ReportTypeEnum(str, Enum):
    """Types of research reports."""

    DISEASE_ANALYSIS = "disease_analysis"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    COST_ANALYSIS = "cost_analysis"
    MARKET_TRENDS = "market_trends"
    GTM_STRATEGY = "gtm_strategy"


class ReportStatusEnum(str, Enum):
    """Report processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ShareTypeEnum(str, Enum):
    """Report sharing types."""

    USER = "user"
    PUBLIC = "public"
    LINK = "link"


class AccessLevelEnum(str, Enum):
    """Access levels for shared reports."""

    READ = "read"
    COMMENT = "comment"
    EDIT = "edit"


class ExportFormatEnum(str, Enum):
    """Export formats for reports."""

    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"


# Request Schemas


class ReportCreateRequest(BaseModel):
    """Base request for creating a research report."""

    title: str = Field(..., min_length=1, max_length=200, description="Report title")
    description: Optional[str] = Field(
        None, max_length=1000, description="Report description"
    )
    crop_types: List[str] = Field(..., description="List of crop types to analyze")
    location: Optional[str] = Field(None, max_length=200, description="Farm location")
    farm_size_acres: Optional[float] = Field(
        None, ge=0.1, le=10000, description="Farm size in acres"
    )


class ReportShareRequest(BaseModel):
    """Request for sharing a report."""

    share_type: ShareTypeEnum = Field(..., description="Type of sharing")
    shared_with_user_id: Optional[int] = Field(
        None, description="User ID to share with (for user sharing)"
    )
    access_level: AccessLevelEnum = Field(
        default=AccessLevelEnum.READ, description="Access level"
    )
    share_message: Optional[str] = Field(
        None, max_length=500, description="Message to include with share"
    )
    expires_at: Optional[datetime] = Field(
        None, description="Expiration date for share"
    )


class ReportExportRequest(BaseModel):
    """Request for exporting a report."""

    export_format: ExportFormatEnum = Field(..., description="Export format")
    export_type: str = Field(
        default="full", description="Export type: full, summary, charts_only"
    )
    include_visualizations: bool = Field(
        default=True, description="Include charts and graphs"
    )
    include_raw_data: bool = Field(default=False, description="Include raw data")
    custom_sections: Optional[List[str]] = Field(
        None, description="Specific sections to include"
    )


class ReportUpdateRequest(BaseModel):
    """Request for updating a report."""

    title: Optional[str] = Field(
        None, min_length=1, max_length=200, description="Updated title"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Updated description"
    )
    is_public: Optional[bool] = Field(None, description="Make report public")
    summary: Optional[str] = Field(None, description="Updated summary")


# Response Schemas


class VisualizationResponse(BaseModel):
    """Response schema for report visualizations."""

    id: int
    chart_type: str
    title: str
    description: Optional[str]
    data_points: Optional[int]
    time_period: Optional[str]
    image_base64: str
    image_format: str
    image_size: Optional[str]
    display_order: int
    is_featured: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ReportSummaryResponse(BaseModel):
    """Summary response for research reports."""

    id: int
    analysis_id: str
    report_type: ReportTypeEnum
    title: str
    description: Optional[str]
    status: ReportStatusEnum
    crop_types: Optional[List[str]]
    location: Optional[str]
    farm_size_acres: Optional[float]
    summary: Optional[str]
    confidence_score: Optional[float]
    visualization_count: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ReportDetailResponse(BaseModel):
    """Detailed response for research reports."""

    id: int
    analysis_id: str
    user_id: int
    crop_id: Optional[int]
    report_type: ReportTypeEnum
    title: str
    description: Optional[str]
    status: ReportStatusEnum

    # Analysis parameters
    crop_types: Optional[List[str]]
    location: Optional[str]
    farm_size_acres: Optional[float]
    analysis_period: Optional[str]

    # Report data
    report_data: Dict[str, Any]
    summary: Optional[str]
    confidence_score: Optional[float]

    # Integration data
    daily_log_id: Optional[int]
    todo_ids: Optional[List[int]]
    integration_status: Optional[str]

    # Processing metadata
    processing_time_seconds: Optional[float]
    error_message: Optional[str]

    # Sharing and access
    is_public: bool
    shared_with_users: Optional[List[int]]

    # Timestamps
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    # Visualizations
    visualizations: List[VisualizationResponse] = []

    class Config:
        from_attributes = True


class DiseaseReportDetailResponse(BaseModel):
    """Detailed response for disease research reports."""

    id: int
    report_id: int

    # Disease identification
    disease_name: Optional[str]
    scientific_name: Optional[str]
    confidence_level: Optional[str]
    confidence_score: Optional[float]
    severity: Optional[str]
    symptoms_observed: Optional[List[str]]
    affected_plant_parts: Optional[List[str]]

    # Environmental analysis
    environmental_factors: Optional[Dict[str, Any]]
    weather_data: Optional[Dict[str, Any]]
    soil_impact: Optional[str]

    # Research findings
    disease_causes: Optional[List[str]]
    pathogen_lifecycle: Optional[str]
    spread_mechanisms: Optional[List[str]]
    host_range: Optional[List[str]]
    research_sources: Optional[List[str]]

    # Treatment and prevention
    treatment_options: Optional[List[Dict[str, Any]]]
    prevention_strategies: Optional[List[Dict[str, Any]]]
    immediate_actions: Optional[List[str]]
    long_term_recommendations: Optional[List[str]]

    # Impact analysis
    potential_yield_loss: Optional[float]
    economic_impact: Optional[str]
    recovery_timeline: Optional[str]
    mitigation_potential: Optional[float]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BusinessReportDetailResponse(BaseModel):
    """Detailed response for business intelligence reports."""

    id: int
    report_id: int

    # Cost analysis
    total_cost_per_acre: Optional[float]
    cost_per_unit: Optional[float]
    cost_breakdown: Optional[Dict[str, Any]]

    # ROI analysis
    total_investment: Optional[float]
    total_revenue: Optional[float]
    net_profit: Optional[float]
    roi_percentage: Optional[float]
    break_even_price: Optional[float]
    payback_period_months: Optional[float]

    # Market analysis
    current_market_price: Optional[float]
    price_trend_30_days: Optional[str]
    price_trend_90_days: Optional[str]
    price_forecast_1_month: Optional[float]
    price_forecast_3_months: Optional[float]
    price_forecast_6_months: Optional[float]
    market_volatility: Optional[str]
    demand_forecast: Optional[str]

    # GTM strategy
    recommended_channels: Optional[List[str]]
    pricing_strategy: Optional[str]
    target_markets: Optional[List[str]]
    competitive_advantages: Optional[List[str]]
    market_entry_timing: Optional[str]

    # Consumer insights
    target_demographics: Optional[List[str]]
    demand_drivers: Optional[List[str]]
    price_sensitivity: Optional[float]
    premium_market_potential: Optional[float]
    organic_demand_trend: Optional[str]

    # Competitive analysis
    market_share_estimate: Optional[float]
    key_competitors: Optional[List[str]]
    competitive_pricing: Optional[Dict[str, Any]]
    differentiation_opportunities: Optional[List[str]]
    market_gaps: Optional[List[str]]

    # Financial projections
    revenue_forecast_1_year: Optional[float]
    profit_projection_1_year: Optional[float]
    working_capital_needs: Optional[float]
    funding_requirements: Optional[float]
    financial_risks: Optional[List[str]]

    # Optimization recommendations
    cost_reduction_opportunities: Optional[List[str]]
    revenue_enhancement_strategies: Optional[List[str]]
    operational_improvements: Optional[List[str]]
    technology_adoption: Optional[List[str]]
    market_expansion_opportunities: Optional[List[str]]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReportShareResponse(BaseModel):
    """Response for report sharing operations."""

    id: int
    report_id: int
    share_type: ShareTypeEnum
    access_level: AccessLevelEnum
    share_token: Optional[str]
    expires_at: Optional[datetime]
    share_message: Optional[str]
    view_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReportExportResponse(BaseModel):
    """Response for report export operations."""

    id: int
    report_id: int
    export_format: ExportFormatEnum
    export_type: str
    file_path: Optional[str]
    file_size_bytes: Optional[int]
    download_count: int
    download_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    """Response for listing reports with pagination."""

    reports: List[ReportSummaryResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


class ReportStatsResponse(BaseModel):
    """Response for report statistics."""

    total_reports: int
    reports_by_type: Dict[str, int]
    reports_by_status: Dict[str, int]
    avg_processing_time: Optional[float]
    avg_confidence_score: Optional[float]
    most_analyzed_crops: List[Dict[str, Union[str, int]]]
    recent_activity: List[Dict[str, Any]]


# Combined response for full report with all details
class FullReportResponse(BaseModel):
    """Complete report response with all related data."""

    report: ReportDetailResponse
    disease_details: Optional[DiseaseReportDetailResponse] = None
    business_details: Optional[BusinessReportDetailResponse] = None
    visualizations: List[VisualizationResponse] = []
    shares: List[ReportShareResponse] = []
    exports: List[ReportExportResponse] = []
