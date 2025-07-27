"""
Disease Analysis MCP Tool

Provides crop disease analysis capabilities through the MCP interface.
Integrates with the existing NammaKrushi disease research services.
"""

import logging
import base64
from typing import Dict, Any, Optional
from ..services.integrated_disease_research_service import (
    get_integrated_disease_service,
)
from ..security.zero_retention import get_zero_retention_proxy

logger = logging.getLogger(__name__)


class DiseaseAnalysisTool:
    """
    MCP tool for crop disease analysis and diagnosis.

    Provides AI-powered disease identification, treatment recommendations,
    and prevention strategies while maintaining zero data retention.
    """

    def __init__(self):
        self.disease_service = get_integrated_disease_service()
        self.zero_retention_proxy = get_zero_retention_proxy()

    async def analyze(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze crop disease from symptoms and optional image.

        Args:
            args: Sanitized arguments containing:
                - crop_type: Type of crop being analyzed
                - symptoms_text: Description of observed symptoms
                - location: Location of the crop (optional)
                - image_base64: Base64 encoded image (optional)

        Returns:
            Disease analysis results with diagnosis and recommendations
        """
        try:
            # Extract and validate required parameters
            crop_type = args.get("crop_type", "").strip()
            symptoms_text = args.get("symptoms_text", "").strip()
            location = args.get("location", "").strip()
            image_base64 = args.get("image_base64", "").strip()

            if not crop_type:
                return {
                    "error": "missing_crop_type",
                    "message": "Crop type is required for disease analysis",
                }

            if not symptoms_text:
                return {
                    "error": "missing_symptoms",
                    "message": "Symptoms description is required for disease analysis",
                }

            # Sanitize location to city level only
            if location:
                location = self.zero_retention_proxy.sanitize_location(location)

            # Prepare analysis request
            analysis_request = {
                "crop_type": crop_type,
                "symptoms_text": symptoms_text,
                "location": location or "Karnataka",  # Default to Karnataka
                "create_logs_and_todos": False,  # No data retention
            }

            # Handle image if provided
            image_file = None
            if image_base64:
                try:
                    # Decode base64 image
                    image_data = base64.b64decode(image_base64)

                    # Create a temporary file-like object for the image
                    from io import BytesIO

                    image_file = BytesIO(image_data)
                    image_file.name = "crop_image.jpg"

                except Exception as e:
                    logger.warning(f"Failed to decode image: {e}")
                    # Continue without image

            # Perform disease analysis
            if image_file:
                # Use image-based analysis
                result = await self.disease_service.analyze_with_image(
                    crop_type=analysis_request["crop_type"],
                    symptoms_text=analysis_request["symptoms_text"],
                    location=analysis_request["location"],
                    image=image_file,
                    create_logs_and_todos=False,
                )
            else:
                # Use text-based analysis
                result = await self.disease_service.analyze_text_only(
                    crop_type=analysis_request["crop_type"],
                    symptoms_text=analysis_request["symptoms_text"],
                    location=analysis_request["location"],
                )

            # Process and format the results
            formatted_result = self._format_disease_analysis_result(result)

            logger.info(f"Disease analysis completed for crop: {crop_type}")
            return formatted_result

        except Exception as e:
            logger.error(f"Error in disease analysis: {e}")
            return {
                "error": "analysis_failed",
                "message": "Unable to complete disease analysis. Please check your inputs and try again.",
                "details": str(e) if logger.isEnabledFor(logging.DEBUG) else None,
            }

    def _format_disease_analysis_result(
        self, raw_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format the disease analysis result for MCP consumption.

        Args:
            raw_result: Raw result from disease service

        Returns:
            Formatted result optimized for MCP clients
        """
        try:
            if raw_result.get("status") != "success":
                return {
                    "error": "analysis_unsuccessful",
                    "message": raw_result.get(
                        "error_message", "Disease analysis was not successful"
                    ),
                }

            report = raw_result.get("report", {})

            # Extract key information
            disease_info = report.get("disease_identification", {})
            environmental_info = report.get("environmental_analysis", {})
            weather_info = report.get("weather_correlation", {})
            treatments = report.get("treatment_options", [])
            prevention = report.get("prevention_strategies", [])
            yield_impact = report.get("yield_impact", {})
            immediate_actions = report.get("immediate_actions", [])
            long_term_recommendations = report.get("long_term_recommendations", [])

            # Format the response
            formatted_result = {
                "status": "success",
                "analysis_summary": {
                    "disease_name": disease_info.get("disease_name", "Unknown"),
                    "scientific_name": disease_info.get("scientific_name", ""),
                    "confidence": disease_info.get("confidence", "unknown"),
                    "confidence_score": disease_info.get("confidence_score", 0),
                    "severity": disease_info.get("severity", "unknown"),
                    "affected_parts": disease_info.get("affected_plant_parts", []),
                },
                "environmental_factors": {
                    "soil_impact": environmental_info.get("soil_ph_impact", ""),
                    "moisture_conditions": environmental_info.get(
                        "moisture_conditions", ""
                    ),
                    "temperature_range": environmental_info.get(
                        "temperature_range", ""
                    ),
                    "humidity_impact": environmental_info.get("humidity_impact", ""),
                    "nutrient_deficiencies": environmental_info.get(
                        "nutrient_deficiencies", []
                    ),
                    "stress_factors": environmental_info.get(
                        "environmental_stress_factors", []
                    ),
                },
                "current_weather": {
                    "location": weather_info.get("location", ""),
                    "temperature_avg": weather_info.get("temperature_avg", 0),
                    "humidity": weather_info.get("humidity", 0),
                    "rainfall": weather_info.get("rainfall", 0),
                    "conditions_favorable": self._assess_weather_favorability(
                        weather_info, disease_info
                    ),
                },
                "treatment_recommendations": [
                    {
                        "name": treatment.get("treatment_name", ""),
                        "type": treatment.get("treatment_type", ""),
                        "method": treatment.get("application_method", ""),
                        "dosage": treatment.get("dosage", ""),
                        "frequency": treatment.get("frequency", ""),
                        "effectiveness": f"{treatment.get('effectiveness', 0) * 100:.1f}%",
                        "cost_estimate": treatment.get("cost_estimate", ""),
                        "availability": treatment.get("availability", ""),
                        "side_effects": treatment.get("side_effects", []),
                    }
                    for treatment in treatments[:3]  # Limit to top 3 treatments
                ],
                "prevention_strategies": [
                    {
                        "strategy": strategy.get("strategy_name", ""),
                        "description": strategy.get("description", ""),
                        "effectiveness": f"{strategy.get('effectiveness', 0) * 100:.1f}%",
                        "cost": strategy.get("cost", ""),
                        "timing": strategy.get("timing", ""),
                    }
                    for strategy in prevention[:3]  # Limit to top 3 strategies
                ],
                "economic_impact": {
                    "potential_yield_loss": f"{yield_impact.get('potential_yield_loss', 0)}%",
                    "economic_impact": yield_impact.get("economic_impact", ""),
                    "recovery_timeline": yield_impact.get("recovery_timeline", ""),
                    "mitigation_potential": f"{yield_impact.get('mitigation_potential', 0) * 100:.1f}%",
                },
                "immediate_actions": immediate_actions[:5],  # Limit to top 5 actions
                "long_term_recommendations": long_term_recommendations[
                    :5
                ],  # Limit to top 5
                "executive_summary": report.get("executive_summary", "").strip(),
            }

            return formatted_result

        except Exception as e:
            logger.error(f"Error formatting disease analysis result: {e}")
            return {
                "error": "formatting_failed",
                "message": "Disease analysis completed but result formatting failed",
                "raw_result": raw_result,
            }

    def _assess_weather_favorability(
        self, weather_info: Dict[str, Any], disease_info: Dict[str, Any]
    ) -> str:
        """
        Assess whether current weather conditions favor disease development.

        Args:
            weather_info: Current weather data
            disease_info: Disease identification data

        Returns:
            Assessment of weather favorability for disease
        """
        try:
            humidity = weather_info.get("humidity", 0)
            temp_avg = weather_info.get("temperature_avg", 0)
            rainfall = weather_info.get("rainfall", 0)

            # General disease-favorable conditions
            high_humidity = humidity > 70
            moderate_temp = 20 <= temp_avg <= 30
            recent_rain = rainfall > 10

            favorable_factors = sum([high_humidity, moderate_temp, recent_rain])

            if favorable_factors >= 2:
                return "High - Current conditions favor disease development"
            elif favorable_factors == 1:
                return "Moderate - Some conditions favor disease development"
            else:
                return "Low - Current conditions are less favorable for disease"

        except Exception:
            return "Unknown - Unable to assess weather favorability"
