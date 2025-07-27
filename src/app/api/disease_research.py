"""
Disease Research API Endpoints

API endpoints for the multi-agent crop disease research system.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import base64

from ..services.deep_research.deep_research_diseaase import (
    deep_research_disease_analysis,
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
router = APIRouter(prefix="/api/disease-research", tags=["Disease Research"])


class DiseaseResearchRequest(BaseModel):
    """Request model for disease research analysis."""

    symptoms_text: Optional[str] = Field(
        None, description="Text description of observed symptoms", max_length=2000
    )
    crop_type: str = Field(
        ..., description="Type of crop being analyzed", max_length=100
    )
    location: Optional[str] = Field(
        None, description="Location of the crop", max_length=200
    )
    crop_id: Optional[int] = Field(
        None,
        description="ID of the crop being analyzed (for linking to daily logs and todos)",
    )
    soil_data: Optional[Dict[str, Any]] = Field(None, description="Soil analysis data")
    weather_data: Optional[Dict[str, Any]] = Field(None, description="Weather data")
    create_logs_and_todos: bool = Field(
        True, description="Whether to create daily log entries and todo tasks"
    )
    crop_type: str = Field(
        ..., description="Type of crop being analyzed", max_length=100
    )
    location: Optional[str] = Field(
        None, description="Location of the crop", max_length=200
    )
    soil_data: Optional[Dict[str, Any]] = Field(None, description="Soil analysis data")
    weather_data: Optional[Dict[str, Any]] = Field(None, description="Weather data")


class DiseaseResearchResponse(BaseModel):
    """Response model for disease research analysis."""

    status: str = Field(..., description="Status of the analysis")
    analysis_id: Optional[str] = Field(None, description="Unique analysis identifier")
    report: Optional[Dict[str, Any]] = Field(
        None, description="Comprehensive disease analysis report"
    )
    error_message: Optional[str] = Field(
        None, description="Error message if analysis failed"
    )


@router.post("/analyze", response_model=DiseaseResearchResponse)
async def analyze_crop_disease(
    request: DiseaseResearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyze crop disease using multi-agent research system.

    This endpoint conducts comprehensive disease analysis including:
    - Disease identification from symptoms
    - Environmental factor correlation
    - Deep research on causes and treatments
    - Treatment recommendations with procedures
    - Yield impact analysis
    - Prevention strategies
    """

    try:
        logger.info(
            f"Starting disease analysis for user {current_user.id}, crop: {request.crop_type}"
        )

        # Verify crop ownership if crop_id is provided
        if request.crop_id:
            crop = (
                db.query(Crop)
                .filter(Crop.id == request.crop_id, Crop.user_id == current_user.id)
                .first()
            )

            if not crop:
                raise HTTPException(
                    status_code=404,
                    detail="Crop not found or you don't have permission to access it",
                )

            logger.info(f"Verified crop ownership: crop_id={request.crop_id}")

        # Conduct deep research analysis with integration
        result = await deep_research_disease_analysis(
            image_data=None,  # No image in this endpoint
            symptoms_text=request.symptoms_text,
            crop_type=request.crop_type,
            location=request.location,
            soil_data=request.soil_data,
            weather_data=request.weather_data,
            user_id=current_user.id,
            crop_id=request.crop_id,
            db=db,
            create_logs_and_todos=request.create_logs_and_todos,
        )

        logger.info(f"Disease analysis completed with status: {result['status']}")

        # Store the report in database if analysis was successful
        if result["status"] == "success" and result.get("report"):
            try:
                report_service = get_report_service(db)
                stored_report = report_service.create_report(
                    user_id=current_user.id,
                    analysis_id=result["analysis_id"],
                    report_type=ReportType.DISEASE_ANALYSIS,
                    report_data=result["report"],
                    crop_id=request.crop_id,
                    title=f"Disease Analysis - {request.crop_type}",
                    description=f"Disease analysis for {request.crop_type} crop",
                    crop_types=[request.crop_type],
                    location=request.location,
                    daily_log_id=result["report"].get("daily_log_id"),
                    todo_ids=result["report"].get("todo_ids", []),
                    integration_status=result["report"].get(
                        "integration_status", "pending"
                    ),
                )
                logger.info(
                    f"Stored disease research report {stored_report.id} in database"
                )
            except Exception as e:
                logger.error(f"Failed to store report in database: {e}")
                # Continue with response even if storage fails

        return DiseaseResearchResponse(
            status=result["status"],
            analysis_id=result.get("analysis_id"),
            report=result.get("report"),
            error_message=result.get("error_message"),
        )

    except Exception as e:
        logger.error(f"Disease analysis API error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Disease analysis failed: {str(e)}"
        )


@router.post("/analyze-with-image", response_model=DiseaseResearchResponse)
async def analyze_crop_disease_with_image(
    crop_type: str = Form(..., description="Type of crop being analyzed"),
    symptoms_text: Optional[str] = Form(
        None, description="Text description of symptoms"
    ),
    location: Optional[str] = Form(None, description="Location of the crop"),
    crop_id: Optional[int] = Form(None, description="ID of the crop being analyzed"),
    create_logs_and_todos: bool = Form(
        True, description="Whether to create daily log entries and todo tasks"
    ),
    image: Optional[UploadFile] = File(None, description="Image of the affected crop"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Analyze crop disease with image upload using multi-agent research system.

    This endpoint accepts an image file along with other parameters for comprehensive analysis.
    """

    try:
        logger.info(
            f"Starting disease analysis with image for user {current_user.id}, crop: {crop_type}"
        )

        # Process image if provided
        image_data = None
        if image:
            # Validate image file
            if not image.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400, detail="Uploaded file must be an image"
                )

            # Read image data
            image_content = await image.read()
            image_data = image_content

            logger.info(
                f"Image uploaded: {image.filename}, size: {len(image_content)} bytes"
            )

        # Verify crop ownership if crop_id is provided
        if crop_id:
            crop = (
                db.query(Crop)
                .filter(Crop.id == crop_id, Crop.user_id == current_user.id)
                .first()
            )

            if not crop:
                raise HTTPException(
                    status_code=404,
                    detail="Crop not found or you don't have permission to access it",
                )

            logger.info(f"Verified crop ownership: crop_id={crop_id}")

        # Conduct deep research analysis with integration
        result = await deep_research_disease_analysis(
            image_data=image_data,
            symptoms_text=symptoms_text,
            crop_type=crop_type,
            location=location,
            soil_data=None,  # Could be added as form field if needed
            weather_data=None,  # Could be added as form field if needed
            user_id=current_user.id,
            crop_id=crop_id,
            db=db,
            create_logs_and_todos=create_logs_and_todos,
        )

        logger.info(
            f"Disease analysis with image completed with status: {result['status']}"
        )

        # Store the report in database if analysis was successful
        if result["status"] == "success" and result.get("report"):
            try:
                report_service = get_report_service(db)
                stored_report = report_service.create_report(
                    user_id=current_user.id,
                    analysis_id=result["analysis_id"],
                    report_type=ReportType.DISEASE_ANALYSIS,
                    report_data=result["report"],
                    crop_id=crop_id,
                    title=f"Disease Analysis with Image - {crop_type}",
                    description=f"Disease analysis with image for {crop_type} crop",
                    crop_types=[crop_type],
                    location=location,
                    daily_log_id=result["report"].get("daily_log_id"),
                    todo_ids=result["report"].get("todo_ids", []),
                    integration_status=result["report"].get(
                        "integration_status", "pending"
                    ),
                )
                logger.info(
                    f"Stored disease research report {stored_report.id} in database"
                )
            except Exception as e:
                logger.error(f"Failed to store report in database: {e}")
                # Continue with response even if storage fails

        return DiseaseResearchResponse(
            status=result["status"],
            analysis_id=result.get("analysis_id"),
            report=result.get("report"),
            error_message=result.get("error_message"),
        )

        logger.info(
            f"Disease analysis with image completed with status: {result['status']}"
        )

        return DiseaseResearchResponse(
            status=result["status"],
            analysis_id=result.get("analysis_id"),
            report=result.get("report"),
            error_message=result.get("error_message"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disease analysis with image API error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Disease analysis failed: {str(e)}"
        )


@router.get("/analysis/{analysis_id}", response_model=ReportDetailResponse)
async def get_analysis_report(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve a previously conducted disease analysis report.
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


@router.get("/reports", response_model=ReportListResponse)
async def list_disease_reports(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all disease research reports for the current user.
    """

    try:
        report_service = get_report_service(db)
        reports, total_count = report_service.get_user_reports(
            user_id=current_user.id,
            report_type=ReportType.DISEASE_ANALYSIS,
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
        logger.error(f"Failed to list disease reports: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list disease reports: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for the disease research service."""

    try:
        # Basic health check - could be expanded to check dependencies
        return {
            "status": "healthy",
            "service": "Disease Research API",
            "version": "1.0.0",
            "features": [
                "Multi-agent disease identification",
                "Environmental factor analysis",
                "Deep research with Exa search",
                "Treatment recommendations",
                "Yield impact analysis",
                "Prevention strategies",
                "Image analysis support",
            ],
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@router.get("/info")
async def get_service_info():
    """Get information about the disease research service capabilities."""

    return {
        "service_name": "Multi-Agent Crop Disease Research System",
        "description": "Comprehensive crop disease analysis using specialized AI agents",
        "agents": {
            "disease_identification": {
                "description": "Identifies diseases from images and symptom descriptions",
                "capabilities": [
                    "image analysis",
                    "symptom interpretation",
                    "confidence scoring",
                ],
            },
            "environmental_analysis": {
                "description": "Analyzes environmental factors contributing to disease",
                "capabilities": [
                    "soil correlation",
                    "weather impact",
                    "stress factor identification",
                ],
            },
            "research_agent": {
                "description": "Conducts deep research using Exa search",
                "capabilities": [
                    "literature search",
                    "cause analysis",
                    "recent developments",
                ],
            },
            "treatment_recommendation": {
                "description": "Provides treatment options and procedures",
                "capabilities": [
                    "chemical treatments",
                    "biological controls",
                    "cultural practices",
                ],
            },
            "yield_impact_analysis": {
                "description": "Assesses economic and yield implications",
                "capabilities": [
                    "loss estimation",
                    "economic impact",
                    "recovery timeline",
                ],
            },
        },
        "supported_inputs": [
            "crop images",
            "symptom descriptions",
            "soil data",
            "weather data",
            "location information",
        ],
        "output_features": [
            "disease identification with confidence",
            "environmental correlation analysis",
            "comprehensive treatment options",
            "prevention strategies",
            "yield impact assessment",
            "economic analysis",
            "actionable recommendations",
        ],
    }
