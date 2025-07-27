"""
Business Intelligence API Endpoints

API endpoints for the multi-agent business intelligence and GTM research system.
"""

import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..services.deep_research.business_intelligence_research import (
    comprehensive_business_intelligence_analysis,
    AnalysisType,
)
from ..services.research_report_service import get_report_service
from ..models.research_report import ReportType
from ..schemas.research_report import ReportDetailResponse, ReportListResponse
from ..utils.auth import get_current_user
from ..models.user import User
from ..models.crop import Crop
from ..config.database import get_db

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/business-intelligence", tags=["Business Intelligence"])


class BusinessAnalysisRequest(BaseModel):
    """Request model for business intelligence analysis."""

    crop_types: List[str] = Field(
        default=["all"],
        description="List of crop types to analyze (use ['all'] for all crops)",
    )
    location: str = Field(
        default="Karnataka", description="Location of the farm"
    )
    farm_size_acres: Optional[float] = Field(
        None, description="Farm size in acres", ge=0.1, le=10000
    )
    analysis_type: AnalysisType = Field(
        default=AnalysisType.COMPREHENSIVE, description="Type of analysis to perform"
    )
    analysis_period_months: int = Field(
        default=12, description="Analysis period in months", ge=1, le=60
    )
    create_logs_and_todos: bool = Field(
        default=True, description="Whether to create daily log entries and todo tasks"
    )


class BusinessAnalysisResponse(BaseModel):
    """Response model for business intelligence analysis."""

    status: str = Field(..., description="Status of the analysis")
    analysis_id: Optional[str] = Field(None, description="Unique analysis identifier")
    report: Optional[Dict[str, Any]] = Field(
        None, description="Comprehensive business analysis report"
    )
    error_message: Optional[str] = Field(
        None, description="Error message if analysis failed"
    )


class QuickInsightsRequest(BaseModel):
    """Request model for quick business insights."""

    crop_type: str = Field(..., description="Single crop type for quick analysis")
    metric_type: str = Field(
        default="roi",
        description="Type of metric to analyze (roi, cost, market_price, trend)",
    )


class DashboardDataResponse(BaseModel):
    """Response model for dashboard data."""

    farmer_id: int = Field(..., description="Farmer ID")
    total_crops: int = Field(..., description="Total number of crops")
    total_revenue: float = Field(..., description="Total revenue")
    total_costs: float = Field(..., description="Total costs")
    overall_roi: float = Field(..., description="Overall ROI percentage")
    top_performing_crop: str = Field(..., description="Best performing crop")
    market_trend: str = Field(..., description="Overall market trend")
    recommendations_count: int = Field(
        ..., description="Number of active recommendations"
    )


@router.post("/analyze", response_model=BusinessAnalysisResponse)
async def conduct_business_analysis(
    request: BusinessAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Conduct comprehensive business intelligence analysis.

    This endpoint provides:
    - Cost analysis and ROI calculations
    - Market trend analysis and price forecasting
    - Go-to-market strategy recommendations
    - Consumer insights and competitive analysis
    - Financial projections and planning
    - Data visualizations and charts
    - Business optimization recommendations
    """

    try:
        logger.info(f"Starting business analysis for user {current_user.id}")

        # Validate crop types if specific crops are requested
        if request.crop_types != ["all"]:
            user_crops = db.query(Crop).filter(Crop.user_id == current_user.id).all()
            user_crop_names = [crop.crop_name.lower() for crop in user_crops]

            invalid_crops = [
                crop
                for crop in request.crop_types
                if crop.lower() not in user_crop_names
            ]
            if invalid_crops:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid crop types: {invalid_crops}. You can only analyze your own crops.",
                )

        # Conduct comprehensive business analysis
        result = await comprehensive_business_intelligence_analysis(
            farmer_id=current_user.id,
            crop_types=request.crop_types,
            location=request.location,
            farm_size=request.farm_size_acres,
            analysis_type=request.analysis_type,
            db=db,
            create_logs_and_todos=request.create_logs_and_todos,
        )

        logger.info(f"Business analysis completed with status: {result['status']}")

        # Store the report in database if analysis was successful
        if result["status"] == "success" and result.get("report"):
            try:
                report_service = get_report_service(db)
                stored_report = report_service.create_report(
                    user_id=current_user.id,
                    analysis_id=result["analysis_id"],
                    report_type=ReportType.BUSINESS_INTELLIGENCE,
                    report_data=result["report"],
                    title=f"Business Intelligence - {', '.join(request.crop_types[:2])}",
                    description=f"Business intelligence analysis for {', '.join(request.crop_types)} crops",
                    crop_types=request.crop_types,
                    location=request.location,
                    farm_size_acres=request.farm_size_acres,
                    daily_log_id=result["report"].get("daily_log_id"),
                    todo_ids=result["report"].get("todo_ids", []),
                    integration_status=result["report"].get(
                        "integration_status", "pending"
                    ),
                )
                logger.info(
                    f"Stored business intelligence report {stored_report.id} in database"
                )
            except Exception as e:
                logger.error(f"Failed to store report in database: {e}")
                # Continue with response even if storage fails

        return BusinessAnalysisResponse(
            status=result["status"],
            analysis_id=result.get("analysis_id"),
            report=result.get("report"),
            error_message=result.get("error_message"),
        )

        logger.info(f"Business analysis completed with status: {result['status']}")

        return BusinessAnalysisResponse(
            status=result["status"],
            analysis_id=result.get("analysis_id"),
            report=result.get("report"),
            error_message=result.get("error_message"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Business analysis API error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Business analysis failed: {str(e)}"
        )


@router.get("/dashboard", response_model=DashboardDataResponse)
async def get_dashboard_data(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get dashboard data for business intelligence overview.

    Provides key metrics and insights for the farmer's dashboard.
    """

    try:
        logger.info(f"Fetching dashboard data for user {current_user.id}")

        # Get user's crops
        user_crops = db.query(Crop).filter(Crop.user_id == current_user.id).all()

        if not user_crops:
            return DashboardDataResponse(
                farmer_id=current_user.id,
                total_crops=0,
                total_revenue=0.0,
                total_costs=0.0,
                overall_roi=0.0,
                top_performing_crop="No crops found",
                market_trend="No data available",
                recommendations_count=0,
            )

        # Calculate basic metrics (simplified for demo)
        total_crops = len(user_crops)
        total_revenue = 50000.0 * total_crops  # Placeholder calculation
        total_costs = 35000.0 * total_crops  # Placeholder calculation
        overall_roi = (
            ((total_revenue - total_costs) / total_costs) * 100
            if total_costs > 0
            else 0
        )

        top_performing_crop = user_crops[0].crop_name if user_crops else "Unknown"
        market_trend = "Stable with growth potential"
        recommendations_count = 5  # Placeholder

        return DashboardDataResponse(
            farmer_id=current_user.id,
            total_crops=total_crops,
            total_revenue=total_revenue,
            total_costs=total_costs,
            overall_roi=overall_roi,
            top_performing_crop=top_performing_crop,
            market_trend=market_trend,
            recommendations_count=recommendations_count,
        )

    except Exception as e:
        logger.error(f"Dashboard data API error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch dashboard data: {str(e)}"
        )


@router.post("/quick-insights")
async def get_quick_insights(
    request: QuickInsightsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get quick business insights for a specific crop and metric.

    Provides rapid analysis for specific business questions.
    """

    try:
        logger.info(
            f"Getting quick insights for {request.crop_type} - {request.metric_type}"
        )

        # Verify user has this crop
        user_crop = (
            db.query(Crop)
            .filter(
                Crop.user_id == current_user.id,
                Crop.crop_name.ilike(f"%{request.crop_type}%"),
            )
            .first()
        )

        if not user_crop:
            raise HTTPException(
                status_code=404,
                detail=f"Crop '{request.crop_type}' not found in your farm",
            )

        # Generate quick insights based on metric type
        insights = {}

        if request.metric_type == "roi":
            insights = {
                "metric": "ROI Analysis",
                "current_value": "25.3%",
                "trend": "increasing",
                "benchmark": "Industry average: 20%",
                "recommendation": "Consider premium pricing strategy to increase ROI",
            }
        elif request.metric_type == "cost":
            insights = {
                "metric": "Cost Analysis",
                "current_value": "₹35,000 per acre",
                "trend": "stable",
                "benchmark": "Regional average: ₹38,000",
                "recommendation": "Optimize fertilizer costs through soil testing",
            }
        elif request.metric_type == "market_price":
            insights = {
                "metric": "Market Price",
                "current_value": "₹28.50 per kg",
                "trend": "increasing",
                "benchmark": "Last month: ₹26.00",
                "recommendation": "Good time to sell, prices expected to remain high",
            }
        elif request.metric_type == "trend":
            insights = {
                "metric": "Market Trend",
                "current_value": "Bullish",
                "trend": "positive",
                "benchmark": "3-month outlook: Strong demand",
                "recommendation": "Increase production for next season",
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid metric_type. Use: roi, cost, market_price, or trend",
            )

        return {
            "status": "success",
            "crop_type": request.crop_type,
            "insights": insights,
            "generated_at": "2024-12-27T14:30:22Z",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quick insights API error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate insights: {str(e)}"
        )


@router.get("/reports/{analysis_id}", response_model=ReportDetailResponse)
async def get_analysis_report(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a previously conducted business analysis report.
    """

    try:
        report_service = get_report_service(db)
        report = report_service.get_report_by_analysis_id(analysis_id, current_user.id)

        if not report:
            raise HTTPException(
                status_code=404,
                detail="Analysis report not found or you don't have permission to access it",
            )

        # Convert to response model
        return ReportDetailResponse(
            id=report.id,
            analysis_id=report.analysis_id,
            user_id=report.user_id,
            crop_id=report.crop_id,
            report_type=report.report_type,
            title=report.title,
            description=report.description,
            status=report.status,
            crop_types=report.crop_types,
            location=report.location,
            farm_size_acres=report.farm_size_acres,
            analysis_period=report.analysis_period,
            report_data=report.report_data,
            summary=report.summary,
            confidence_score=report.confidence_score,
            daily_log_id=report.daily_log_id,
            todo_ids=report.todo_ids,
            integration_status=report.integration_status,
            processing_time_seconds=report.processing_time_seconds,
            error_message=report.error_message,
            is_public=report.is_public,
            shared_with_users=report.shared_with_users,
            created_at=report.created_at,
            updated_at=report.updated_at,
            completed_at=report.completed_at,
            visualizations=[
                {
                    "id": viz.id,
                    "chart_type": viz.chart_type,
                    "title": viz.title,
                    "description": viz.description,
                    "data_points": viz.data_points,
                    "time_period": viz.time_period,
                    "image_base64": viz.image_base64,
                    "image_format": viz.image_format,
                    "image_size": viz.image_size,
                    "display_order": viz.display_order,
                    "is_featured": viz.is_featured,
                    "created_at": viz.created_at,
                }
                for viz in report.chart_visualizations
            ],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve analysis report: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve analysis report: {str(e)}"
        )


@router.get("/visualizations/{analysis_id}")
async def get_analysis_visualizations(
    analysis_id: str,
    chart_type: str = Query(
        ..., description="Type of chart: cost_breakdown, price_trend, roi_analysis"
    ),
    current_user: User = Depends(get_current_user),
):
    """
    Get specific visualizations from a business analysis.

    Returns base64 encoded chart images.
    """

    try:
        # This would typically retrieve stored visualizations
        # For now, return a placeholder response

        return {
            "status": "success",
            "analysis_id": analysis_id,
            "chart_type": chart_type,
            "chart_data": {
                "title": f"{chart_type.replace('_', ' ').title()} Chart",
                "description": f"Visualization for {chart_type}",
                "image_base64": "",  # Would contain actual chart data
                "metadata": {
                    "generated_at": "2024-12-27T14:30:22Z",
                    "data_points": 10,
                    "time_period": "Last 12 months",
                },
            },
        }

    except Exception as e:
        logger.error(f"Visualization retrieval error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve visualization: {str(e)}"
        )


@router.get("/market-data")
async def get_market_data(
    crop_type: str = Query(..., description="Crop type for market data"),
    location: str = Query(default="Karnataka", description="Location for market data"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current market data for a specific crop and location.

    Provides real-time market information.
    """

    try:
        logger.info(f"Fetching market data for {crop_type} in {location}")

        # This would typically query real market data
        # For now, return sample data

        market_data = {
            "crop_type": crop_type,
            "location": location,
            "current_price": 28.50,
            "price_change_24h": 2.3,
            "price_change_percentage": 8.8,
            "volume_traded": 1250,
            "market_trend": "bullish",
            "demand_level": "high",
            "supply_level": "moderate",
            "quality_premium": 15.0,
            "forecast_7_days": {
                "expected_price": 30.25,
                "confidence": 0.75,
                "trend": "increasing",
            },
            "last_updated": "2024-12-27T14:30:22Z",
        }

        return {"status": "success", "market_data": market_data}

    except Exception as e:
        logger.error(f"Market data API error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch market data: {str(e)}"
        )


@router.get("/recommendations")
async def get_business_recommendations(
    current_user: User = Depends(get_current_user),
    category: str = Query(
        default="all",
        description="Recommendation category: cost, revenue, market, technology",
    ),
    priority: str = Query(
        default="all", description="Priority level: high, medium, low"
    ),
):
    """
    Get personalized business recommendations for the farmer.

    Returns actionable recommendations based on farm data and market conditions.
    """

    try:
        logger.info(f"Fetching recommendations for user {current_user.id}")

        # Sample recommendations (would be generated from actual analysis)
        all_recommendations = [
            {
                "id": 1,
                "category": "cost",
                "priority": "high",
                "title": "Optimize Fertilizer Usage",
                "description": "Reduce fertilizer costs by 15% through soil testing and precision application",
                "potential_savings": 5000,
                "implementation_time": "2 weeks",
                "difficulty": "medium",
            },
            {
                "id": 2,
                "category": "revenue",
                "priority": "high",
                "title": "Direct Sales Channel",
                "description": "Establish direct-to-consumer sales to increase profit margins by 25%",
                "potential_revenue": 12000,
                "implementation_time": "1 month",
                "difficulty": "medium",
            },
            {
                "id": 3,
                "category": "market",
                "priority": "medium",
                "title": "Premium Market Entry",
                "description": "Target organic certification to access premium market segment",
                "potential_revenue": 20000,
                "implementation_time": "6 months",
                "difficulty": "high",
            },
            {
                "id": 4,
                "category": "technology",
                "priority": "medium",
                "title": "IoT Monitoring System",
                "description": "Implement IoT sensors for precision agriculture and cost optimization",
                "potential_savings": 8000,
                "implementation_time": "3 months",
                "difficulty": "high",
            },
        ]

        # Filter recommendations based on query parameters
        filtered_recommendations = all_recommendations

        if category != "all":
            filtered_recommendations = [
                r for r in filtered_recommendations if r["category"] == category
            ]

        if priority != "all":
            filtered_recommendations = [
                r for r in filtered_recommendations if r["priority"] == priority
            ]

        return {
            "status": "success",
            "total_recommendations": len(filtered_recommendations),
            "recommendations": filtered_recommendations,
            "filters_applied": {"category": category, "priority": priority},
        }

    except Exception as e:
        logger.error(f"Recommendations API error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch recommendations: {str(e)}"
        )


@router.get("/reports", response_model=ReportListResponse)
async def list_business_reports(
    page: int = 1,
    page_size: int = 20,
    analysis_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all business intelligence reports for the current user.
    """

    try:
        report_service = get_report_service(db)

        # Map analysis type to report type
        report_type = None
        if analysis_type == "cost_analysis":
            report_type = ReportType.COST_ANALYSIS
        elif analysis_type == "market_trends":
            report_type = ReportType.MARKET_TRENDS
        elif analysis_type == "gtm_strategy":
            report_type = ReportType.GTM_STRATEGY
        else:
            report_type = ReportType.BUSINESS_INTELLIGENCE

        reports, total_count = report_service.get_user_reports(
            user_id=current_user.id,
            report_type=report_type,
            page=page,
            page_size=page_size,
        )

        total_pages = (total_count + page_size - 1) // page_size

        report_summaries = [
            {
                "id": report.id,
                "analysis_id": report.analysis_id,
                "report_type": report.report_type,
                "title": report.title,
                "description": report.description,
                "status": report.status,
                "crop_types": report.crop_types,
                "location": report.location,
                "farm_size_acres": report.farm_size_acres,
                "summary": report.summary,
                "confidence_score": report.confidence_score,
                "visualization_count": len(report.chart_visualizations),
                "created_at": report.created_at,
                "updated_at": report.updated_at,
                "completed_at": report.completed_at,
            }
            for report in reports
        ]

        return ReportListResponse(
            reports=report_summaries,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )

    except Exception as e:
        logger.error(f"Failed to list business reports: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list business reports: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for the business intelligence service."""

    try:
        return {
            "status": "healthy",
            "service": "Business Intelligence API",
            "version": "1.0.0",
            "features": [
                "Comprehensive business analysis",
                "Cost analysis and ROI calculations",
                "Market trend analysis and forecasting",
                "GTM strategy development",
                "Consumer insights and competitive analysis",
                "Financial projections and planning",
                "Data visualizations and charts",
                "Business optimization recommendations",
                "Real-time dashboard data",
                "Quick insights and market data",
            ],
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@router.get("/info")
async def get_service_info():
    """Get information about the business intelligence service capabilities."""

    return {
        "service_name": "Multi-Agent Business Intelligence & GTM Research System",
        "description": "Comprehensive business analysis using specialized AI agents for farmer success",
        "agents": {
            "cost_analysis": {
                "description": "Analyzes input costs, operational expenses, and ROI calculations",
                "capabilities": [
                    "cost breakdown",
                    "ROI analysis",
                    "break-even calculations",
                    "profitability assessment",
                ],
            },
            "market_trend_analysis": {
                "description": "Analyzes market trends and provides price forecasting",
                "capabilities": [
                    "price forecasting",
                    "demand analysis",
                    "seasonal trends",
                    "volatility assessment",
                ],
            },
            "gtm_strategy": {
                "description": "Develops go-to-market strategies and channel recommendations",
                "capabilities": [
                    "channel strategy",
                    "pricing strategy",
                    "market positioning",
                    "competitive analysis",
                ],
            },
            "consumer_insights": {
                "description": "Analyzes consumer behavior and demand patterns",
                "capabilities": [
                    "demand analysis",
                    "price sensitivity",
                    "quality preferences",
                    "market segmentation",
                ],
            },
            "data_visualization": {
                "description": "Creates charts and graphs for data presentation",
                "capabilities": [
                    "cost charts",
                    "trend analysis",
                    "ROI visualizations",
                    "market data charts",
                ],
            },
            "business_optimization": {
                "description": "Provides recommendations for business improvement",
                "capabilities": [
                    "cost reduction",
                    "revenue enhancement",
                    "operational efficiency",
                    "technology adoption",
                ],
            },
        },
        "analysis_types": [
            "comprehensive",
            "cost_analysis",
            "market_trends",
            "gtm_strategy",
            "consumer_insights",
            "competitive_analysis",
            "financial_planning",
        ],
        "supported_outputs": [
            "detailed cost breakdown",
            "ROI and profitability analysis",
            "market trend forecasts",
            "GTM strategy recommendations",
            "consumer behavior insights",
            "competitive landscape analysis",
            "financial projections",
            "data visualizations",
            "optimization recommendations",
            "actionable business plans",
        ],
        "integration_features": [
            "daily log integration",
            "todo task generation",
            "dashboard data",
            "real-time market data",
            "personalized recommendations",
        ],
    }
