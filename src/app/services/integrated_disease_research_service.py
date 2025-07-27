"""
Integrated Disease Research Service

Service that combines the deep research disease analysis with automatic database storage
and research report management.
"""

import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from .deep_research.deep_research_diseaase import deep_research_disease_analysis
from .research_report_service import get_report_service
from ..models.research_report import ReportType
from ..models.user import User
from ..models.crop import Crop
from ..utils.json_serializer import clean_report_data

logger = logging.getLogger(__name__)


class IntegratedDiseaseResearchService:
    """Service that integrates disease research with database storage."""

    def __init__(self, db: Session):
        self.db = db
        self.report_service = get_report_service(db)

    async def analyze_disease_with_storage(
        self,
        user_id: int,
        crop_type: str,
        image_data: Optional[bytes] = None,
        symptoms_text: Optional[str] = None,
        location: Optional[str] = None,
        crop_id: Optional[int] = None,
        soil_data: Optional[Dict[str, Any]] = None,
        weather_data: Optional[Dict[str, Any]] = None,
        create_logs_and_todos: bool = True,
        auto_store_report: bool = True,
    ) -> Dict[str, Any]:
        """
        Conduct disease analysis and automatically store results in database.

        Args:
            user_id: ID of the user conducting the analysis
            crop_type: Type of crop being analyzed
            image_data: Optional image data of affected crop
            symptoms_text: Text description of symptoms
            location: Location of the crop
            crop_id: Optional crop ID for linking
            soil_data: Soil analysis data
            weather_data: Weather data
            create_logs_and_todos: Whether to create daily logs and todos
            auto_store_report: Whether to automatically store the report

        Returns:
            Dict containing analysis results and database storage info
        """

        try:
            logger.info(
                f"Starting integrated disease analysis for user {user_id}, crop: {crop_type}"
            )

            # Verify crop ownership if crop_id provided
            if crop_id:
                crop = (
                    self.db.query(Crop)
                    .filter(Crop.id == crop_id, Crop.user_id == user_id)
                    .first()
                )
                if not crop:
                    return {
                        "status": "error",
                        "error_message": "Crop not found or access denied",
                        "analysis_id": None,
                        "report": None,
                        "database_report_id": None,
                    }

            # Conduct the disease analysis
            analysis_result = await deep_research_disease_analysis(
                image_data=image_data,
                symptoms_text=symptoms_text,
                crop_type=crop_type,
                location=location,
                soil_data=soil_data,
                weather_data=weather_data,
                user_id=user_id,
                crop_id=crop_id,
                db=self.db,
                create_logs_and_todos=create_logs_and_todos,
            )

            # If analysis failed, return the error
            if analysis_result["status"] != "success":
                return analysis_result

            # Store the report in database if requested and analysis was successful
            database_report_id = None
            if auto_store_report and analysis_result.get("report"):
                try:
                    # Clean the report data before storing
                    report_data = analysis_result["report"]
                    cleaned_report_data = clean_report_data(report_data)

                    stored_report = self.report_service.create_report(
                        user_id=user_id,
                        analysis_id=analysis_result["analysis_id"],
                        report_type=ReportType.DISEASE_ANALYSIS,
                        report_data=cleaned_report_data,  # Use cleaned data
                        crop_id=crop_id,
                        title=f"Disease Analysis - {crop_type}"
                        + (" (with Image)" if image_data else ""),
                        description=f"Comprehensive disease analysis for {crop_type} crop"
                        + (f" in {location}" if location else ""),
                        crop_types=[crop_type],
                        location=location,
                        daily_log_id=report_data.get("daily_log_id"),
                        todo_ids=report_data.get("todo_ids", []),
                        integration_status=report_data.get(
                            "integration_status", "pending"
                        ),
                    )

                    database_report_id = stored_report.id
                    logger.info(
                        f"Successfully stored disease research report {database_report_id}"
                    )

                    # Add database info to the response
                    analysis_result["report"]["database_report_id"] = database_report_id
                    analysis_result["database_report_id"] = database_report_id

                except Exception as e:
                    logger.error(f"Failed to store disease research report: {e}")
                    return {
                        "status": "error",
                        "error_message": f"Analysis completed but failed to save to database: {str(e)}",
                        "analysis_id": analysis_result.get("analysis_id"),
                        "report": analysis_result.get("report"),
                        "database_report_id": None,
                    }

            # Add storage status to response
            analysis_result["database_storage"] = {
                "stored": auto_store_report,
                "report_id": database_report_id,
                "status": "success" if database_report_id else "skipped",
            }

            logger.info(
                f"Integrated disease analysis completed successfully: {analysis_result['analysis_id']}"
            )
            return analysis_result

        except Exception as e:
            logger.error(f"Integrated disease analysis failed: {e}")
            return {
                "status": "error",
                "error_message": f"Integrated analysis failed: {str(e)}",
                "analysis_id": None,
                "report": None,
                "database_report_id": None,
            }

    async def get_user_disease_reports(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        include_details: bool = False,
    ) -> Dict[str, Any]:
        """
        Get disease research reports for a user.

        Args:
            user_id: User ID
            page: Page number
            page_size: Number of reports per page
            include_details: Whether to include full report details

        Returns:
            Dict containing reports and pagination info
        """

        try:
            reports, total_count = self.report_service.get_user_reports(
                user_id=user_id,
                report_type=ReportType.DISEASE_ANALYSIS,
                page=page,
                page_size=page_size,
            )

            total_pages = (total_count + page_size - 1) // page_size

            report_data = []
            for report in reports:
                report_info = {
                    "id": report.id,
                    "analysis_id": report.analysis_id,
                    "title": report.title,
                    "description": report.description,
                    "status": report.status.value,
                    "crop_types": report.crop_types,
                    "location": report.location,
                    "summary": report.summary,
                    "confidence_score": report.confidence_score,
                    "created_at": report.created_at.isoformat(),
                    "updated_at": report.updated_at.isoformat()
                    if report.updated_at
                    else None,
                    "completed_at": report.completed_at.isoformat()
                    if report.completed_at
                    else None,
                    "integration_status": report.integration_status,
                    "daily_log_id": report.daily_log_id,
                    "todo_count": len(report.todo_ids) if report.todo_ids else 0,
                    "visualization_count": len(report.chart_visualizations),
                }

                # Include full details if requested
                if include_details:
                    report_info["report_data"] = report.report_data
                    report_info["visualizations"] = [
                        {
                            "id": viz.id,
                            "chart_type": viz.chart_type,
                            "title": viz.title,
                            "description": viz.description,
                            "image_base64": viz.image_base64,
                        }
                        for viz in report.chart_visualizations
                    ]

                report_data.append(report_info)

            return {
                "status": "success",
                "reports": report_data,
                "pagination": {
                    "total_count": total_count,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_previous": page > 1,
                },
            }

        except Exception as e:
            logger.error(f"Failed to get user disease reports: {e}")
            return {
                "status": "error",
                "error_message": f"Failed to retrieve reports: {str(e)}",
                "reports": [],
                "pagination": None,
            }

    async def get_disease_report_by_id(
        self,
        report_id: int,
        user_id: int,
        include_visualizations: bool = True,
    ) -> Dict[str, Any]:
        """
        Get a specific disease research report by ID.

        Args:
            report_id: Report ID
            user_id: User ID (for access control)
            include_visualizations: Whether to include visualization data

        Returns:
            Dict containing the report data
        """

        try:
            report = self.report_service.get_report_by_id(report_id, user_id)

            if not report:
                return {
                    "status": "error",
                    "error_message": "Report not found or access denied",
                    "report": None,
                }

            if report.report_type != ReportType.DISEASE_ANALYSIS:
                return {
                    "status": "error",
                    "error_message": "Report is not a disease analysis report",
                    "report": None,
                }

            report_data = {
                "id": report.id,
                "analysis_id": report.analysis_id,
                "user_id": report.user_id,
                "crop_id": report.crop_id,
                "title": report.title,
                "description": report.description,
                "status": report.status.value,
                "crop_types": report.crop_types,
                "location": report.location,
                "farm_size_acres": report.farm_size_acres,
                "analysis_period": report.analysis_period,
                "summary": report.summary,
                "confidence_score": report.confidence_score,
                "daily_log_id": report.daily_log_id,
                "todo_ids": report.todo_ids,
                "integration_status": report.integration_status,
                "processing_time_seconds": report.processing_time_seconds,
                "is_public": report.is_public,
                "shared_with_users": report.shared_with_users,
                "created_at": report.created_at.isoformat(),
                "updated_at": report.updated_at.isoformat()
                if report.updated_at
                else None,
                "completed_at": report.completed_at.isoformat()
                if report.completed_at
                else None,
                "report_data": report.report_data,
            }

            # Include visualizations if requested
            if include_visualizations:
                report_data["visualizations"] = [
                    {
                        "id": viz.id,
                        "chart_type": viz.chart_type,
                        "title": viz.title,
                        "description": viz.description,
                        "data_points": viz.data_points,
                        "time_period": viz.time_period,
                        "image_base64": viz.image_base64,
                        "image_format": viz.image_format,
                        "display_order": viz.display_order,
                        "created_at": viz.created_at.isoformat(),
                    }
                    for viz in report.chart_visualizations
                ]

            return {
                "status": "success",
                "report": report_data,
            }

        except Exception as e:
            logger.error(f"Failed to get disease report {report_id}: {e}")
            return {
                "status": "error",
                "error_message": f"Failed to retrieve report: {str(e)}",
                "report": None,
            }

    async def get_disease_analysis_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Get statistics for user's disease analysis reports.

        Args:
            user_id: User ID

        Returns:
            Dict containing statistics
        """

        try:
            # Get all disease reports for the user
            all_reports, total_count = self.report_service.get_user_reports(
                user_id=user_id,
                report_type=ReportType.DISEASE_ANALYSIS,
                page=1,
                page_size=1000,  # Get all reports for statistics
            )

            # Calculate statistics
            stats = {
                "total_analyses": total_count,
                "analyses_with_images": 0,
                "analyses_with_todos": 0,
                "analyses_with_daily_logs": 0,
                "avg_confidence_score": 0.0,
                "most_analyzed_crops": {},
                "most_common_diseases": {},
                "severity_distribution": {},
                "recent_analyses": [],
            }

            if total_count > 0:
                confidence_scores = []
                crop_counts = {}
                disease_counts = {}
                severity_counts = {}

                for report in all_reports:
                    # Count analyses with images (check if title contains "with Image")
                    if "with Image" in report.title:
                        stats["analyses_with_images"] += 1

                    # Count analyses with todos and daily logs
                    if report.todo_ids:
                        stats["analyses_with_todos"] += 1
                    if report.daily_log_id:
                        stats["analyses_with_daily_logs"] += 1

                    # Collect confidence scores
                    if report.confidence_score:
                        confidence_scores.append(report.confidence_score)

                    # Count crops
                    if report.crop_types:
                        for crop in report.crop_types:
                            crop_counts[crop] = crop_counts.get(crop, 0) + 1

                    # Extract disease and severity info from report data
                    if report.report_data:
                        disease_id = report.report_data.get(
                            "disease_identification", {}
                        )
                        if disease_id.get("disease_name"):
                            disease_name = disease_id["disease_name"]
                            disease_counts[disease_name] = (
                                disease_counts.get(disease_name, 0) + 1
                            )

                        if disease_id.get("severity"):
                            severity = disease_id["severity"]
                            severity_counts[severity] = (
                                severity_counts.get(severity, 0) + 1
                            )

                # Calculate averages
                if confidence_scores:
                    stats["avg_confidence_score"] = sum(confidence_scores) / len(
                        confidence_scores
                    )

                # Get top crops and diseases
                stats["most_analyzed_crops"] = dict(
                    sorted(crop_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                )
                stats["most_common_diseases"] = dict(
                    sorted(disease_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                )
                stats["severity_distribution"] = severity_counts

                # Get recent analyses
                stats["recent_analyses"] = [
                    {
                        "id": report.id,
                        "analysis_id": report.analysis_id,
                        "title": report.title,
                        "crop_types": report.crop_types,
                        "confidence_score": report.confidence_score,
                        "created_at": report.created_at.isoformat(),
                    }
                    for report in all_reports[:5]  # Most recent 5
                ]

            return {
                "status": "success",
                "statistics": stats,
            }

        except Exception as e:
            logger.error(f"Failed to get disease analysis statistics: {e}")
            return {
                "status": "error",
                "error_message": f"Failed to retrieve statistics: {str(e)}",
                "statistics": None,
            }


def get_integrated_disease_service(db: Session) -> IntegratedDiseaseResearchService:
    """Get the integrated disease research service."""
    return IntegratedDiseaseResearchService(db)
