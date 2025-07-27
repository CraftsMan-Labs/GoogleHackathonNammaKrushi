"""
Research Report Service

Service layer for managing research reports including storage, retrieval, sharing, and export functionality.
"""

import logging
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from ..models.research_report import (
    ResearchReport,
    DiseaseResearchReport,
    BusinessIntelligenceReport,
    ReportVisualization,
    ReportShare,
    ReportExport,
    ReportType,
    ReportStatus,
)
from ..models.user import User
from ..models.crop import Crop
from ..schemas.research_report import (
    ReportCreateRequest,
    ReportShareRequest,
    ReportExportRequest,
    ReportUpdateRequest,
    ReportDetailResponse,
    ReportSummaryResponse,
    ReportListResponse,
    ReportStatsResponse,
    FullReportResponse,
)

logger = logging.getLogger(__name__)


class ResearchReportService:
    """Service for managing research reports."""

    def __init__(self, db: Session):
        self.db = db

    def create_report(
        self,
        user_id: int,
        analysis_id: str,
        report_type: ReportType,
        report_data: Dict[str, Any],
        crop_id: Optional[int] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        crop_types: Optional[List[str]] = None,
        location: Optional[str] = None,
        farm_size_acres: Optional[float] = None,
        daily_log_id: Optional[int] = None,
        todo_ids: Optional[List[int]] = None,
        integration_status: str = "pending",
    ) -> ResearchReport:
        """Create a new research report."""

        try:
            # Extract summary and confidence from report data
            summary = report_data.get("executive_summary", "")
            confidence_score = report_data.get("confidence_score", 0.0)

            # Create main report
            report = ResearchReport(
                analysis_id=analysis_id,
                user_id=user_id,
                crop_id=crop_id,
                report_type=report_type,
                title=title or f"{report_type.value.replace('_', ' ').title()} Report",
                description=description,
                status=ReportStatus.COMPLETED,
                crop_types=crop_types,
                location=location,
                farm_size_acres=farm_size_acres,
                analysis_period="Last 12 months",
                report_data=report_data,
                summary=summary,
                confidence_score=confidence_score,
                daily_log_id=daily_log_id,
                todo_ids=todo_ids or [],
                integration_status=integration_status,
                completed_at=datetime.now(),
            )

            self.db.add(report)
            self.db.flush()  # Get the ID without committing

            # Create specific report details based on type
            if report_type == ReportType.DISEASE_ANALYSIS:
                self._create_disease_report_details(report.id, report_data)
            elif report_type == ReportType.BUSINESS_INTELLIGENCE:
                self._create_business_report_details(report.id, report_data)

            # Create visualizations
            self._create_visualizations(
                report.id, report_data.get("visualizations", [])
            )

            self.db.commit()
            self.db.refresh(report)

            logger.info(f"Created research report {report.id} for user {user_id}")
            return report

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create research report: {e}")
            raise

    def _create_disease_report_details(
        self, report_id: int, report_data: Dict[str, Any]
    ):
        """Create disease-specific report details."""

        disease_id = report_data.get("disease_identification", {})
        environmental = report_data.get("environmental_analysis", {})
        research = report_data.get("research_findings", {})
        treatments = report_data.get("treatment_options", [])
        prevention = report_data.get("prevention_strategies", [])
        yield_impact = report_data.get("yield_impact", {})

        disease_report = DiseaseResearchReport(
            report_id=report_id,
            disease_name=disease_id.get("disease_name"),
            scientific_name=disease_id.get("scientific_name"),
            confidence_level=disease_id.get("confidence"),
            confidence_score=disease_id.get("confidence_score"),
            severity=disease_id.get("severity"),
            symptoms_observed=disease_id.get("symptoms_observed", []),
            affected_plant_parts=disease_id.get("affected_plant_parts", []),
            environmental_factors=environmental,
            weather_data=report_data.get("weather_correlation"),
            soil_impact=environmental.get("soil_ph_impact"),
            disease_causes=research.get("disease_causes", []),
            pathogen_lifecycle=research.get("pathogen_lifecycle"),
            spread_mechanisms=research.get("spread_mechanisms", []),
            host_range=research.get("host_range", []),
            research_sources=research.get("research_sources", []),
            treatment_options=treatments,
            prevention_strategies=prevention,
            immediate_actions=report_data.get("immediate_actions", []),
            long_term_recommendations=report_data.get("long_term_recommendations", []),
            potential_yield_loss=yield_impact.get("potential_yield_loss"),
            economic_impact=yield_impact.get("economic_impact"),
            recovery_timeline=yield_impact.get("recovery_timeline"),
            mitigation_potential=yield_impact.get("mitigation_potential"),
        )

        self.db.add(disease_report)

    def _create_business_report_details(
        self, report_id: int, report_data: Dict[str, Any]
    ):
        """Create business intelligence-specific report details."""

        cost_analysis = report_data.get("cost_analysis", {})
        roi_analysis = report_data.get("roi_analysis", {})
        market_trends = report_data.get("market_trends", {})
        gtm_strategy = report_data.get("gtm_strategy", {})
        consumer_insights = report_data.get("consumer_insights", {})
        competitive = report_data.get("competitive_analysis", {})
        financial = report_data.get("financial_projections", {})
        optimization = report_data.get("optimization_recommendations", {})

        business_report = BusinessIntelligenceReport(
            report_id=report_id,
            total_cost_per_acre=cost_analysis.get("total_cost_per_acre"),
            cost_per_unit=cost_analysis.get("cost_per_unit"),
            cost_breakdown=cost_analysis,
            total_investment=roi_analysis.get("total_investment"),
            total_revenue=roi_analysis.get("total_revenue"),
            net_profit=roi_analysis.get("net_profit"),
            roi_percentage=roi_analysis.get("roi_percentage"),
            break_even_price=roi_analysis.get("break_even_price"),
            payback_period_months=roi_analysis.get("payback_period_months"),
            current_market_price=market_trends.get("current_price"),
            price_trend_30_days=market_trends.get("price_trend_30_days"),
            price_trend_90_days=market_trends.get("price_trend_90_days"),
            price_forecast_1_month=market_trends.get("price_forecast_1_month"),
            price_forecast_3_months=market_trends.get("price_forecast_3_months"),
            price_forecast_6_months=market_trends.get("price_forecast_6_months"),
            market_volatility=market_trends.get("market_volatility"),
            demand_forecast=market_trends.get("demand_forecast"),
            recommended_channels=gtm_strategy.get("recommended_channels", []),
            pricing_strategy=gtm_strategy.get("pricing_strategy"),
            target_markets=gtm_strategy.get("target_markets", []),
            competitive_advantages=gtm_strategy.get("competitive_advantages", []),
            market_entry_timing=gtm_strategy.get("market_entry_timing"),
            target_demographics=consumer_insights.get("target_demographics", []),
            demand_drivers=consumer_insights.get("demand_drivers", []),
            price_sensitivity=consumer_insights.get("price_sensitivity"),
            premium_market_potential=consumer_insights.get("premium_market_potential"),
            organic_demand_trend=consumer_insights.get("organic_demand_trend"),
            market_share_estimate=competitive.get("market_share_estimate"),
            key_competitors=competitive.get("key_competitors", []),
            competitive_pricing=competitive.get("competitive_pricing", {}),
            differentiation_opportunities=competitive.get(
                "differentiation_opportunities", []
            ),
            market_gaps=competitive.get("market_gaps", []),
            revenue_forecast_1_year=financial.get("revenue_forecast_1_year"),
            profit_projection_1_year=financial.get("profit_projection_1_year"),
            working_capital_needs=financial.get("working_capital_needs"),
            funding_requirements=financial.get("funding_requirements"),
            financial_risks=financial.get("financial_risks", []),
            cost_reduction_opportunities=optimization.get(
                "cost_reduction_opportunities", []
            ),
            revenue_enhancement_strategies=optimization.get(
                "revenue_enhancement_strategies", []
            ),
            operational_improvements=optimization.get("operational_improvements", []),
            technology_adoption=optimization.get("technology_adoption", []),
            market_expansion_opportunities=optimization.get(
                "market_expansion_opportunities", []
            ),
        )

        self.db.add(business_report)

    def _create_visualizations(
        self, report_id: int, visualizations: List[Dict[str, Any]]
    ):
        """Create visualization records for the report."""

        for i, viz_data in enumerate(visualizations):
            visualization = ReportVisualization(
                report_id=report_id,
                chart_type=viz_data.get("chart_type", "unknown"),
                title=viz_data.get("title", f"Chart {i+1}"),
                description=viz_data.get("description"),
                data_points=viz_data.get("data_points"),
                time_period=viz_data.get("time_period"),
                chart_data={},  # Could store raw data if needed
                image_base64=viz_data.get("image_base64", ""),
                image_format="png",
                display_order=i,
            )
            self.db.add(visualization)

    def get_report_by_id(
        self, report_id: int, user_id: int
    ) -> Optional[ResearchReport]:
        """Get a report by ID, ensuring user has access."""

        return (
            self.db.query(ResearchReport)
            .filter(
                and_(
                    ResearchReport.id == report_id,
                    or_(
                        ResearchReport.user_id == user_id,
                        ResearchReport.is_public == True,
                        ResearchReport.shared_with_users.contains([user_id]),
                    ),
                )
            )
            .first()
        )

    def get_report_by_analysis_id(
        self, analysis_id: str, user_id: int
    ) -> Optional[ResearchReport]:
        """Get a report by analysis ID."""

        return (
            self.db.query(ResearchReport)
            .filter(
                and_(
                    ResearchReport.analysis_id == analysis_id,
                    or_(
                        ResearchReport.user_id == user_id,
                        ResearchReport.is_public == True,
                        ResearchReport.shared_with_users.contains([user_id]),
                    ),
                )
            )
            .first()
        )

    def get_user_reports(
        self,
        user_id: int,
        report_type: Optional[ReportType] = None,
        status: Optional[ReportStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[ResearchReport], int]:
        """Get reports for a user with pagination."""

        query = self.db.query(ResearchReport).filter(ResearchReport.user_id == user_id)

        if report_type:
            query = query.filter(ResearchReport.report_type == report_type)

        if status:
            query = query.filter(ResearchReport.status == status)

        query = query.order_by(desc(ResearchReport.created_at))

        total_count = query.count()

        offset = (page - 1) * page_size
        reports = query.offset(offset).limit(page_size).all()

        return reports, total_count

    def update_report(
        self, report_id: int, user_id: int, update_data: ReportUpdateRequest
    ) -> Optional[ResearchReport]:
        """Update a report."""

        report = (
            self.db.query(ResearchReport)
            .filter(
                and_(ResearchReport.id == report_id, ResearchReport.user_id == user_id)
            )
            .first()
        )

        if not report:
            return None

        # Update fields
        if update_data.title is not None:
            report.title = update_data.title
        if update_data.description is not None:
            report.description = update_data.description
        if update_data.is_public is not None:
            report.is_public = update_data.is_public
        if update_data.summary is not None:
            report.summary = update_data.summary

        report.updated_at = datetime.now()

        self.db.commit()
        self.db.refresh(report)

        return report

    def delete_report(self, report_id: int, user_id: int) -> bool:
        """Delete a report."""

        report = (
            self.db.query(ResearchReport)
            .filter(
                and_(ResearchReport.id == report_id, ResearchReport.user_id == user_id)
            )
            .first()
        )

        if not report:
            return False

        self.db.delete(report)
        self.db.commit()

        logger.info(f"Deleted research report {report_id} for user {user_id}")
        return True

    def share_report(
        self, report_id: int, user_id: int, share_request: ReportShareRequest
    ) -> Optional[ReportShare]:
        """Share a report with another user or make it public."""

        report = (
            self.db.query(ResearchReport)
            .filter(
                and_(ResearchReport.id == report_id, ResearchReport.user_id == user_id)
            )
            .first()
        )

        if not report:
            return None

        # Generate share token for link sharing
        share_token = None
        if share_request.share_type == "link":
            share_token = str(uuid.uuid4())

        share = ReportShare(
            report_id=report_id,
            shared_by_user_id=user_id,
            shared_with_user_id=share_request.shared_with_user_id,
            share_type=share_request.share_type,
            access_level=share_request.access_level,
            share_token=share_token,
            expires_at=share_request.expires_at,
            share_message=share_request.share_message,
        )

        self.db.add(share)

        # Update report sharing settings
        if share_request.share_type == "public":
            report.is_public = True
        elif share_request.shared_with_user_id:
            shared_users = report.shared_with_users or []
            if share_request.shared_with_user_id not in shared_users:
                shared_users.append(share_request.shared_with_user_id)
                report.shared_with_users = shared_users

        self.db.commit()
        self.db.refresh(share)

        return share

    def get_report_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get statistics for user's reports."""

        # Total reports
        total_reports = (
            self.db.query(ResearchReport)
            .filter(ResearchReport.user_id == user_id)
            .count()
        )

        # Reports by type
        reports_by_type = {}
        for report_type in ReportType:
            count = (
                self.db.query(ResearchReport)
                .filter(
                    and_(
                        ResearchReport.user_id == user_id,
                        ResearchReport.report_type == report_type,
                    )
                )
                .count()
            )
            reports_by_type[report_type.value] = count

        # Reports by status
        reports_by_status = {}
        for status in ReportStatus:
            count = (
                self.db.query(ResearchReport)
                .filter(
                    and_(
                        ResearchReport.user_id == user_id,
                        ResearchReport.status == status,
                    )
                )
                .count()
            )
            reports_by_status[status.value] = count

        # Average processing time and confidence
        avg_stats = (
            self.db.query(
                func.avg(ResearchReport.processing_time_seconds),
                func.avg(ResearchReport.confidence_score),
            )
            .filter(
                and_(
                    ResearchReport.user_id == user_id,
                    ResearchReport.status == ReportStatus.COMPLETED,
                )
            )
            .first()
        )

        avg_processing_time = avg_stats[0] if avg_stats[0] else 0
        avg_confidence_score = avg_stats[1] if avg_stats[1] else 0

        # Most analyzed crops
        # This would require a more complex query to count crop occurrences
        most_analyzed_crops = [
            {"crop": "tomato", "count": 5},
            {"crop": "rice", "count": 3},
            {"crop": "wheat", "count": 2},
        ]

        # Recent activity
        recent_reports = (
            self.db.query(ResearchReport)
            .filter(ResearchReport.user_id == user_id)
            .order_by(desc(ResearchReport.created_at))
            .limit(5)
            .all()
        )

        recent_activity = [
            {
                "id": report.id,
                "title": report.title,
                "type": report.report_type.value,
                "created_at": report.created_at.isoformat(),
            }
            for report in recent_reports
        ]

        return {
            "total_reports": total_reports,
            "reports_by_type": reports_by_type,
            "reports_by_status": reports_by_status,
            "avg_processing_time": avg_processing_time,
            "avg_confidence_score": avg_confidence_score,
            "most_analyzed_crops": most_analyzed_crops,
            "recent_activity": recent_activity,
        }

    def export_report(
        self, report_id: int, user_id: int, export_request: ReportExportRequest
    ) -> Optional[ReportExport]:
        """Export a report in the specified format."""

        report = self.get_report_by_id(report_id, user_id)
        if not report:
            return None

        # Create export record
        export = ReportExport(
            report_id=report_id,
            user_id=user_id,
            export_format=export_request.export_format,
            export_type=export_request.export_type,
            include_visualizations=export_request.include_visualizations,
            include_raw_data=export_request.include_raw_data,
            custom_sections=export_request.custom_sections,
        )

        # Generate export file (this would be implemented based on format)
        file_path = self._generate_export_file(report, export_request)
        export.file_path = file_path

        self.db.add(export)
        self.db.commit()
        self.db.refresh(export)

        return export

    def _generate_export_file(
        self, report: ResearchReport, export_request: ReportExportRequest
    ) -> str:
        """Generate export file based on format and options."""

        # This would implement actual file generation
        # For now, return a placeholder path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{report.analysis_id}_{timestamp}.{export_request.export_format.value}"
        return f"/exports/{filename}"


# Global service instance
_report_service = None


def get_report_service(db: Session) -> ResearchReportService:
    """Get or create the report service instance."""
    return ResearchReportService(db)
