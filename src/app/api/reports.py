"""
Report Management API Endpoints

Comprehensive API for managing research reports including sharing, export, and analytics.
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from ..services.research_report_service import get_report_service
from ..models.research_report import ReportType, ReportStatus
from ..schemas.research_report import (
    ReportDetailResponse,
    ReportListResponse,
    ReportStatsResponse,
    ReportShareRequest,
    ReportShareResponse,
    ReportExportRequest,
    ReportExportResponse,
    ReportUpdateRequest,
    FullReportResponse,
)
from ..utils.auth import get_current_user
from ..models.user import User
from ..config.database import get_db

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/reports", tags=["Report Management"])


@router.get("/", response_model=ReportListResponse)
async def list_all_reports(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    report_type: Optional[ReportType] = Query(
        None, description="Filter by report type"
    ),
    status: Optional[ReportStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all reports for the current user with filtering and pagination.
    """

    try:
        report_service = get_report_service(db)
        reports, total_count = report_service.get_user_reports(
            user_id=current_user.id,
            report_type=report_type,
            status=status,
            page=page,
            page_size=page_size,
        )

        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            reports = [
                report
                for report in reports
                if (report.title and search_lower in report.title.lower())
                or (report.description and search_lower in report.description.lower())
            ]
            total_count = len(reports)

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
        logger.error(f"Failed to list reports: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")


@router.get("/{report_id}", response_model=FullReportResponse)
async def get_report_details(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a specific report including all related data.
    """

    try:
        report_service = get_report_service(db)
        report = report_service.get_report_by_id(report_id, current_user.id)

        if not report:
            raise HTTPException(
                status_code=404,
                detail="Report not found or you don't have permission to access it",
            )

        # Build comprehensive response
        report_detail = ReportDetailResponse(
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
            visualizations=[],
        )

        # Add visualizations
        visualizations = [
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
        ]

        # Get disease or business details
        disease_details = None
        business_details = None

        if report.disease_reports:
            disease_report = report.disease_reports[0]
            disease_details = {
                "id": disease_report.id,
                "report_id": disease_report.report_id,
                "disease_name": disease_report.disease_name,
                "scientific_name": disease_report.scientific_name,
                "confidence_level": disease_report.confidence_level,
                "confidence_score": disease_report.confidence_score,
                "severity": disease_report.severity,
                "symptoms_observed": disease_report.symptoms_observed,
                "affected_plant_parts": disease_report.affected_plant_parts,
                "environmental_factors": disease_report.environmental_factors,
                "weather_data": disease_report.weather_data,
                "soil_impact": disease_report.soil_impact,
                "disease_causes": disease_report.disease_causes,
                "pathogen_lifecycle": disease_report.pathogen_lifecycle,
                "spread_mechanisms": disease_report.spread_mechanisms,
                "host_range": disease_report.host_range,
                "research_sources": disease_report.research_sources,
                "treatment_options": disease_report.treatment_options,
                "prevention_strategies": disease_report.prevention_strategies,
                "immediate_actions": disease_report.immediate_actions,
                "long_term_recommendations": disease_report.long_term_recommendations,
                "potential_yield_loss": disease_report.potential_yield_loss,
                "economic_impact": disease_report.economic_impact,
                "recovery_timeline": disease_report.recovery_timeline,
                "mitigation_potential": disease_report.mitigation_potential,
                "created_at": disease_report.created_at,
                "updated_at": disease_report.updated_at,
            }

        if report.business_reports:
            business_report = report.business_reports[0]
            business_details = {
                "id": business_report.id,
                "report_id": business_report.report_id,
                "total_cost_per_acre": business_report.total_cost_per_acre,
                "cost_per_unit": business_report.cost_per_unit,
                "cost_breakdown": business_report.cost_breakdown,
                "total_investment": business_report.total_investment,
                "total_revenue": business_report.total_revenue,
                "net_profit": business_report.net_profit,
                "roi_percentage": business_report.roi_percentage,
                "break_even_price": business_report.break_even_price,
                "payback_period_months": business_report.payback_period_months,
                "current_market_price": business_report.current_market_price,
                "price_trend_30_days": business_report.price_trend_30_days,
                "price_trend_90_days": business_report.price_trend_90_days,
                "price_forecast_1_month": business_report.price_forecast_1_month,
                "price_forecast_3_months": business_report.price_forecast_3_months,
                "price_forecast_6_months": business_report.price_forecast_6_months,
                "market_volatility": business_report.market_volatility,
                "demand_forecast": business_report.demand_forecast,
                "recommended_channels": business_report.recommended_channels,
                "pricing_strategy": business_report.pricing_strategy,
                "target_markets": business_report.target_markets,
                "competitive_advantages": business_report.competitive_advantages,
                "market_entry_timing": business_report.market_entry_timing,
                "target_demographics": business_report.target_demographics,
                "demand_drivers": business_report.demand_drivers,
                "price_sensitivity": business_report.price_sensitivity,
                "premium_market_potential": business_report.premium_market_potential,
                "organic_demand_trend": business_report.organic_demand_trend,
                "market_share_estimate": business_report.market_share_estimate,
                "key_competitors": business_report.key_competitors,
                "competitive_pricing": business_report.competitive_pricing,
                "differentiation_opportunities": business_report.differentiation_opportunities,
                "market_gaps": business_report.market_gaps,
                "revenue_forecast_1_year": business_report.revenue_forecast_1_year,
                "profit_projection_1_year": business_report.profit_projection_1_year,
                "working_capital_needs": business_report.working_capital_needs,
                "funding_requirements": business_report.funding_requirements,
                "financial_risks": business_report.financial_risks,
                "cost_reduction_opportunities": business_report.cost_reduction_opportunities,
                "revenue_enhancement_strategies": business_report.revenue_enhancement_strategies,
                "operational_improvements": business_report.operational_improvements,
                "technology_adoption": business_report.technology_adoption,
                "market_expansion_opportunities": business_report.market_expansion_opportunities,
                "created_at": business_report.created_at,
                "updated_at": business_report.updated_at,
            }

        return FullReportResponse(
            report=report_detail,
            disease_details=disease_details,
            business_details=business_details,
            visualizations=visualizations,
            shares=[],  # Would include share information
            exports=[],  # Would include export information
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get report details: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get report details: {str(e)}"
        )


@router.put("/{report_id}", response_model=ReportDetailResponse)
async def update_report(
    report_id: int,
    update_request: ReportUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update a report's metadata.
    """

    try:
        report_service = get_report_service(db)
        updated_report = report_service.update_report(
            report_id=report_id, user_id=current_user.id, update_data=update_request
        )

        if not updated_report:
            raise HTTPException(
                status_code=404,
                detail="Report not found or you don't have permission to update it",
            )

        return ReportDetailResponse(
            id=updated_report.id,
            analysis_id=updated_report.analysis_id,
            user_id=updated_report.user_id,
            crop_id=updated_report.crop_id,
            report_type=updated_report.report_type,
            title=updated_report.title,
            description=updated_report.description,
            status=updated_report.status,
            crop_types=updated_report.crop_types,
            location=updated_report.location,
            farm_size_acres=updated_report.farm_size_acres,
            analysis_period=updated_report.analysis_period,
            report_data=updated_report.report_data,
            summary=updated_report.summary,
            confidence_score=updated_report.confidence_score,
            daily_log_id=updated_report.daily_log_id,
            todo_ids=updated_report.todo_ids,
            integration_status=updated_report.integration_status,
            processing_time_seconds=updated_report.processing_time_seconds,
            error_message=updated_report.error_message,
            is_public=updated_report.is_public,
            shared_with_users=updated_report.shared_with_users,
            created_at=updated_report.created_at,
            updated_at=updated_report.updated_at,
            completed_at=updated_report.completed_at,
            visualizations=[],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update report: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update report: {str(e)}"
        )


@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a report.
    """

    try:
        report_service = get_report_service(db)
        success = report_service.delete_report(report_id, current_user.id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail="Report not found or you don't have permission to delete it",
            )

        return {"status": "success", "message": "Report deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete report: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to delete report: {str(e)}"
        )


@router.post("/{report_id}/share", response_model=ReportShareResponse)
async def share_report(
    report_id: int,
    share_request: ReportShareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Share a report with another user or make it public.
    """

    try:
        report_service = get_report_service(db)
        share = report_service.share_report(
            report_id=report_id, user_id=current_user.id, share_request=share_request
        )

        if not share:
            raise HTTPException(
                status_code=404,
                detail="Report not found or you don't have permission to share it",
            )

        return ReportShareResponse(
            id=share.id,
            report_id=share.report_id,
            share_type=share.share_type,
            access_level=share.access_level,
            share_token=share.share_token,
            expires_at=share.expires_at,
            share_message=share.share_message,
            view_count=share.view_count,
            created_at=share.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to share report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to share report: {str(e)}")


@router.post("/{report_id}/export", response_model=ReportExportResponse)
async def export_report(
    report_id: int,
    export_request: ReportExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Export a report in the specified format.
    """

    try:
        report_service = get_report_service(db)
        export = report_service.export_report(
            report_id=report_id, user_id=current_user.id, export_request=export_request
        )

        if not export:
            raise HTTPException(
                status_code=404,
                detail="Report not found or you don't have permission to export it",
            )

        # Generate download URL (this would be implemented based on file storage)
        download_url = f"/api/reports/exports/{export.id}/download"

        return ReportExportResponse(
            id=export.id,
            report_id=export.report_id,
            export_format=export.export_format,
            export_type=export.export_type,
            file_path=export.file_path,
            file_size_bytes=export.file_size_bytes,
            download_count=export.download_count,
            download_url=download_url,
            created_at=export.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export report: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to export report: {str(e)}"
        )


@router.get("/statistics/overview", response_model=ReportStatsResponse)
async def get_report_statistics(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Get comprehensive statistics about the user's reports.
    """

    try:
        report_service = get_report_service(db)
        stats = report_service.get_report_statistics(current_user.id)

        return ReportStatsResponse(
            total_reports=stats["total_reports"],
            reports_by_type=stats["reports_by_type"],
            reports_by_status=stats["reports_by_status"],
            avg_processing_time=stats["avg_processing_time"],
            avg_confidence_score=stats["avg_confidence_score"],
            most_analyzed_crops=stats["most_analyzed_crops"],
            recent_activity=stats["recent_activity"],
        )

    except Exception as e:
        logger.error(f"Failed to get report statistics: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get report statistics: {str(e)}"
        )


@router.get("/visualizations/{report_id}")
async def get_report_visualizations(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all visualizations for a specific report.
    """

    try:
        report_service = get_report_service(db)
        report = report_service.get_report_by_id(report_id, current_user.id)

        if not report:
            raise HTTPException(
                status_code=404,
                detail="Report not found or you don't have permission to access it",
            )

        visualizations = [
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
        ]

        return {
            "status": "success",
            "report_id": report_id,
            "total_visualizations": len(visualizations),
            "visualizations": visualizations,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get report visualizations: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get report visualizations: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for the report management service."""

    return {
        "status": "healthy",
        "service": "Report Management API",
        "version": "1.0.0",
        "features": [
            "Report storage and retrieval",
            "Report sharing and collaboration",
            "Report export in multiple formats",
            "Report analytics and statistics",
            "Visualization management",
            "Search and filtering",
            "Access control and permissions",
        ],
    }
