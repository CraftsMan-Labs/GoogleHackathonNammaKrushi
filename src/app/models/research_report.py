"""
Research Report Database Models

Models for storing deep research reports including disease analysis and business intelligence reports.
"""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    JSON,
    Boolean,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from ..config.database import Base


class ReportType(enum.Enum):
    """Types of research reports."""

    DISEASE_ANALYSIS = "disease_analysis"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    COST_ANALYSIS = "cost_analysis"
    MARKET_TRENDS = "market_trends"
    GTM_STRATEGY = "gtm_strategy"


class ReportStatus(enum.Enum):
    """Report processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchReport(Base):
    """Main research report table for storing all types of deep research reports."""

    __tablename__ = "research_reports"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=True)

    # Report metadata
    report_type = Column(SQLEnum(ReportType), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING)

    # Analysis parameters
    crop_types = Column(JSON)  # List of crop types analyzed
    location = Column(String)
    farm_size_acres = Column(Float)
    analysis_period = Column(String)

    # Report data (stored as JSON for flexibility)
    report_data = Column(JSON, nullable=False)  # Complete report structure
    summary = Column(Text)  # Executive summary
    confidence_score = Column(Float)

    # Visualizations
    visualizations = Column(JSON)  # List of visualization metadata and base64 data

    # Integration data
    daily_log_id = Column(Integer, ForeignKey("daily_logs.id"), nullable=True)
    todo_ids = Column(JSON)  # List of created todo task IDs
    integration_status = Column(String, default="pending")

    # Processing metadata
    processing_time_seconds = Column(Float)
    error_message = Column(Text)

    # Sharing and access
    is_public = Column(Boolean, default=False)
    shared_with_users = Column(JSON)  # List of user IDs with access
    export_formats = Column(JSON)  # Available export formats

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="research_reports")
    crop = relationship("Crop", back_populates="research_reports")
    daily_log = relationship("DailyLog", back_populates="research_reports")

    # Report-specific relationships
    disease_reports = relationship(
        "DiseaseResearchReport",
        back_populates="main_report",
        cascade="all, delete-orphan",
    )
    business_reports = relationship(
        "BusinessIntelligenceReport",
        back_populates="main_report",
        cascade="all, delete-orphan",
    )


class DiseaseResearchReport(Base):
    """Specific table for disease research report details."""

    __tablename__ = "disease_research_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("research_reports.id"), nullable=False)

    # Disease identification
    disease_name = Column(String)
    scientific_name = Column(String)
    confidence_level = Column(String)  # high, medium, low, uncertain
    confidence_score = Column(Float)
    severity = Column(String)  # mild, moderate, severe, critical
    symptoms_observed = Column(JSON)  # List of symptoms
    affected_plant_parts = Column(JSON)  # List of affected parts

    # Environmental analysis
    environmental_factors = Column(JSON)  # Environmental factor analysis
    weather_data = Column(JSON)  # Weather correlation data
    soil_impact = Column(Text)  # Soil condition impact

    # Research findings
    disease_causes = Column(JSON)  # List of causes
    pathogen_lifecycle = Column(Text)
    spread_mechanisms = Column(JSON)  # List of spread methods
    host_range = Column(JSON)  # Other affected crops
    research_sources = Column(JSON)  # List of research source URLs

    # Treatment and prevention
    treatment_options = Column(JSON)  # List of treatment options
    prevention_strategies = Column(JSON)  # List of prevention strategies
    immediate_actions = Column(JSON)  # List of immediate actions
    long_term_recommendations = Column(JSON)  # List of long-term recommendations

    # Impact analysis
    potential_yield_loss = Column(Float)  # Percentage
    economic_impact = Column(Text)
    recovery_timeline = Column(String)
    mitigation_potential = Column(Float)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    main_report = relationship("ResearchReport", back_populates="disease_reports")


class BusinessIntelligenceReport(Base):
    """Specific table for business intelligence report details."""

    __tablename__ = "business_intelligence_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("research_reports.id"), nullable=False)

    # Cost analysis
    total_cost_per_acre = Column(Float)
    cost_per_unit = Column(Float)
    cost_breakdown = Column(JSON)  # Detailed cost breakdown

    # ROI analysis
    total_investment = Column(Float)
    total_revenue = Column(Float)
    net_profit = Column(Float)
    roi_percentage = Column(Float)
    break_even_price = Column(Float)
    payback_period_months = Column(Float)

    # Market analysis
    current_market_price = Column(Float)
    price_trend_30_days = Column(String)
    price_trend_90_days = Column(String)
    price_forecast_1_month = Column(Float)
    price_forecast_3_months = Column(Float)
    price_forecast_6_months = Column(Float)
    market_volatility = Column(String)
    demand_forecast = Column(String)

    # GTM strategy
    recommended_channels = Column(JSON)  # List of sales channels
    pricing_strategy = Column(Text)
    target_markets = Column(JSON)  # List of target markets
    competitive_advantages = Column(JSON)  # List of advantages
    market_entry_timing = Column(String)

    # Consumer insights
    target_demographics = Column(JSON)  # List of demographics
    demand_drivers = Column(JSON)  # List of demand drivers
    price_sensitivity = Column(Float)
    premium_market_potential = Column(Float)
    organic_demand_trend = Column(String)

    # Competitive analysis
    market_share_estimate = Column(Float)
    key_competitors = Column(JSON)  # List of competitors
    competitive_pricing = Column(JSON)  # Competitor pricing data
    differentiation_opportunities = Column(JSON)  # List of opportunities
    market_gaps = Column(JSON)  # List of market gaps

    # Financial projections
    revenue_forecast_1_year = Column(Float)
    profit_projection_1_year = Column(Float)
    working_capital_needs = Column(Float)
    funding_requirements = Column(Float)
    financial_risks = Column(JSON)  # List of risks

    # Optimization recommendations
    cost_reduction_opportunities = Column(JSON)  # List of opportunities
    revenue_enhancement_strategies = Column(JSON)  # List of strategies
    operational_improvements = Column(JSON)  # List of improvements
    technology_adoption = Column(JSON)  # List of technologies
    market_expansion_opportunities = Column(JSON)  # List of opportunities

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    main_report = relationship("ResearchReport", back_populates="business_reports")


class ReportVisualization(Base):
    """Table for storing report visualizations separately for better management."""

    __tablename__ = "report_visualizations"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("research_reports.id"), nullable=False)

    # Visualization metadata
    chart_type = Column(
        String, nullable=False
    )  # pie_chart, line_chart, bar_chart, etc.
    title = Column(String, nullable=False)
    description = Column(Text)
    data_points = Column(Integer)
    time_period = Column(String)

    # Chart data
    chart_data = Column(JSON)  # Raw data used to generate chart
    image_base64 = Column(Text)  # Base64 encoded image
    image_format = Column(String, default="png")  # png, jpg, svg
    image_size = Column(String)  # dimensions like "800x600"

    # Display settings
    display_order = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    color_scheme = Column(String)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    report = relationship("ResearchReport", backref="chart_visualizations")


class ReportShare(Base):
    """Table for managing report sharing and access permissions."""

    __tablename__ = "report_shares"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("research_reports.id"), nullable=False)
    shared_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shared_with_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Sharing settings
    share_type = Column(String, nullable=False)  # user, public, link
    access_level = Column(String, default="read")  # read, comment, edit
    share_token = Column(String, unique=True, nullable=True)  # For link sharing
    expires_at = Column(DateTime, nullable=True)

    # Sharing metadata
    share_message = Column(Text)
    view_count = Column(Integer, default=0)
    last_viewed_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    report = relationship("ResearchReport", backref="shares")
    shared_by = relationship(
        "User", foreign_keys=[shared_by_user_id], backref="shared_reports"
    )
    shared_with = relationship(
        "User", foreign_keys=[shared_with_user_id], backref="received_reports"
    )


class ReportExport(Base):
    """Table for tracking report exports and downloads."""

    __tablename__ = "report_exports"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("research_reports.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Export details
    export_format = Column(String, nullable=False)  # pdf, excel, csv, json
    export_type = Column(String, nullable=False)  # full, summary, charts_only
    file_path = Column(String)  # Path to exported file
    file_size_bytes = Column(Integer)
    download_count = Column(Integer, default=0)

    # Export settings
    include_visualizations = Column(Boolean, default=True)
    include_raw_data = Column(Boolean, default=False)
    custom_sections = Column(JSON)  # Selected sections to include

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    last_downloaded_at = Column(DateTime)

    # Relationships
    report = relationship("ResearchReport", backref="exports")
    user = relationship("User", backref="report_exports")


# Update existing models to include relationships

# Add to User model (this would be added to the existing user.py file)
# research_reports = relationship("ResearchReport", back_populates="user")

# Add to Crop model (this would be added to the existing crop.py file)
# research_reports = relationship("ResearchReport", back_populates="crop")

# Add to DailyLog model (this would be added to the existing daily_log.py file)
# research_reports = relationship("ResearchReport", back_populates="daily_log")
