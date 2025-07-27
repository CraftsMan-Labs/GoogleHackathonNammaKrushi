"""
Soil Analysis MCP Tools

Provides soil analysis and recommendations through the MCP interface.
Integrates with existing NammaKrushi soil analysis services.
"""

import logging
from typing import Dict, Any, Optional
from ..tools.soil_analysis import get_soilgrids_data
from ..security.zero_retention import get_zero_retention_proxy

logger = logging.getLogger(__name__)


class SoilAnalysisTool:
    """
    MCP tool for soil analysis and agricultural recommendations.

    Provides soil property analysis, crop suitability assessment,
    and management recommendations while maintaining zero data retention.
    """

    def __init__(self):
        self.zero_retention_proxy = get_zero_retention_proxy()

    async def analyze(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze soil properties and provide agricultural recommendations.

        Args:
            args: Sanitized arguments containing:
                - latitude: Latitude coordinate (required)
                - longitude: Longitude coordinate (required)

        Returns:
            Soil analysis with agricultural recommendations
        """
        try:
            # Extract and validate coordinates
            latitude = args.get("latitude")
            longitude = args.get("longitude")

            if latitude is None or longitude is None:
                return {
                    "error": "missing_coordinates",
                    "message": "Both latitude and longitude coordinates are required for soil analysis",
                }

            # Validate coordinate ranges
            if not (-90 <= latitude <= 90):
                return {
                    "error": "invalid_latitude",
                    "message": "Latitude must be between -90 and 90 degrees",
                }

            if not (-180 <= longitude <= 180):
                return {
                    "error": "invalid_longitude",
                    "message": "Longitude must be between -180 and 180 degrees",
                }

            # Get soil data from SoilGrids
            soil_data = await get_soilgrids_data(latitude, longitude)

            if not soil_data or soil_data.get("status") != "success":
                return {
                    "error": "soil_data_unavailable",
                    "message": "Unable to retrieve soil data for the specified coordinates",
                }

            # Format soil analysis for agricultural use
            formatted_result = self._format_soil_analysis(
                soil_data, latitude, longitude
            )

            logger.info(
                f"Soil analysis completed for coordinates: {latitude}, {longitude}"
            )
            return formatted_result

        except Exception as e:
            logger.error(f"Error in soil analysis: {e}")
            return {
                "error": "soil_analysis_failed",
                "message": "Unable to complete soil analysis. Please check coordinates and try again.",
                "details": str(e) if logger.isEnabledFor(logging.DEBUG) else None,
            }

    def _format_soil_analysis(
        self, soil_data: Dict[str, Any], latitude: float, longitude: float
    ) -> Dict[str, Any]:
        """
        Format soil data for agricultural analysis.

        Args:
            soil_data: Raw soil data from SoilGrids service
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Formatted soil analysis with agricultural insights
        """
        try:
            data = soil_data.get("data", {})

            # Extract soil properties
            properties = data.get("properties", {})

            # Get soil property values (using mean values from depth ranges)
            ph_water = self._extract_soil_value(properties.get("phh2o", {}))
            organic_carbon = self._extract_soil_value(properties.get("soc", {}))
            clay_content = self._extract_soil_value(properties.get("clay", {}))
            sand_content = self._extract_soil_value(properties.get("sand", {}))
            silt_content = self._extract_soil_value(properties.get("silt", {}))
            bulk_density = self._extract_soil_value(properties.get("bdod", {}))
            cation_exchange = self._extract_soil_value(properties.get("cec", {}))
            nitrogen = self._extract_soil_value(properties.get("nitrogen", {}))

            # Generate agricultural insights
            agricultural_insights = self._generate_soil_insights(
                ph_water,
                organic_carbon,
                clay_content,
                sand_content,
                silt_content,
                bulk_density,
                cation_exchange,
                nitrogen,
            )

            formatted_result = {
                "status": "success",
                "coordinates": {"latitude": latitude, "longitude": longitude},
                "soil_properties": {
                    "ph_water": {
                        "value": ph_water,
                        "interpretation": self._interpret_ph(ph_water),
                        "unit": "pH units",
                    },
                    "organic_carbon": {
                        "value": organic_carbon,
                        "interpretation": self._interpret_organic_carbon(
                            organic_carbon
                        ),
                        "unit": "g/kg",
                    },
                    "texture": {
                        "clay_percent": clay_content,
                        "sand_percent": sand_content,
                        "silt_percent": silt_content,
                        "soil_type": self._determine_soil_texture(
                            clay_content, sand_content, silt_content
                        ),
                    },
                    "bulk_density": {
                        "value": bulk_density,
                        "interpretation": self._interpret_bulk_density(bulk_density),
                        "unit": "kg/dm³",
                    },
                    "cation_exchange_capacity": {
                        "value": cation_exchange,
                        "interpretation": self._interpret_cec(cation_exchange),
                        "unit": "cmol/kg",
                    },
                },
                "agricultural_assessment": {
                    "fertility_level": agricultural_insights["fertility"],
                    "drainage_characteristics": agricultural_insights["drainage"],
                    "water_holding_capacity": agricultural_insights["water_retention"],
                    "nutrient_availability": agricultural_insights["nutrients"],
                    "tillage_requirements": agricultural_insights["tillage"],
                },
                "crop_suitability": agricultural_insights["crop_suitability"],
                "management_recommendations": agricultural_insights["recommendations"],
                "improvement_strategies": agricultural_insights["improvements"],
            }

            return formatted_result

        except Exception as e:
            logger.error(f"Error formatting soil analysis: {e}")
            return {
                "error": "formatting_failed",
                "message": "Soil data retrieved but formatting failed",
                "raw_data": soil_data,
            }

    def _extract_soil_value(self, property_data: Dict[str, Any]) -> float:
        """Extract mean soil property value from depth ranges."""
        try:
            # Get the first depth range (usually 0-5cm or 0-30cm)
            if property_data and "mean" in property_data:
                values = property_data["mean"]
                if values and len(values) > 0:
                    return float(values[0])
            return 0.0
        except (KeyError, ValueError, TypeError):
            return 0.0

    def _interpret_ph(self, ph_value: float) -> str:
        """Interpret soil pH value for agricultural purposes."""
        if ph_value < 5.5:
            return "Strongly acidic - May limit nutrient availability"
        elif ph_value < 6.0:
            return "Moderately acidic - Suitable for acid-loving crops"
        elif ph_value < 7.0:
            return "Slightly acidic - Good for most crops"
        elif ph_value < 7.5:
            return "Neutral - Optimal for most crops"
        elif ph_value < 8.0:
            return "Slightly alkaline - May affect some nutrients"
        else:
            return "Alkaline - May cause nutrient deficiencies"

    def _interpret_organic_carbon(self, oc_value: float) -> str:
        """Interpret organic carbon content."""
        if oc_value < 5:
            return "Very low - Needs organic matter addition"
        elif oc_value < 10:
            return "Low - Consider organic amendments"
        elif oc_value < 20:
            return "Moderate - Adequate organic matter"
        else:
            return "High - Good organic matter content"

    def _interpret_bulk_density(self, bd_value: float) -> str:
        """Interpret bulk density for soil compaction assessment."""
        if bd_value > 1.6:
            return "High - Soil compaction likely"
        elif bd_value > 1.4:
            return "Moderate - Some compaction possible"
        else:
            return "Low - Good soil structure"

    def _interpret_cec(self, cec_value: float) -> str:
        """Interpret cation exchange capacity."""
        if cec_value < 10:
            return "Low - Limited nutrient holding capacity"
        elif cec_value < 20:
            return "Moderate - Fair nutrient retention"
        else:
            return "High - Good nutrient holding capacity"

    def _determine_soil_texture(self, clay: float, sand: float, silt: float) -> str:
        """Determine soil texture class from particle size distribution."""
        try:
            # Normalize percentages
            total = clay + sand + silt
            if total > 0:
                clay_pct = (clay / total) * 100
                sand_pct = (sand / total) * 100
                silt_pct = (silt / total) * 100
            else:
                return "Unknown"

            # Simplified texture classification
            if clay_pct > 40:
                return "Clay"
            elif clay_pct > 25:
                if sand_pct > 45:
                    return "Sandy clay"
                elif silt_pct > 40:
                    return "Silty clay"
                else:
                    return "Clay loam"
            elif sand_pct > 70:
                return "Sand"
            elif sand_pct > 50:
                if clay_pct > 15:
                    return "Sandy clay loam"
                else:
                    return "Sandy loam"
            elif silt_pct > 50:
                if clay_pct > 15:
                    return "Silty clay loam"
                else:
                    return "Silt loam"
            else:
                return "Loam"

        except Exception:
            return "Unknown"

    def _generate_soil_insights(
        self,
        ph_water: float,
        organic_carbon: float,
        clay_content: float,
        sand_content: float,
        silt_content: float,
        bulk_density: float,
        cation_exchange: float,
        nitrogen: float,
    ) -> Dict[str, Any]:
        """Generate comprehensive agricultural insights from soil data."""

        insights = {
            "fertility": "",
            "drainage": "",
            "water_retention": "",
            "nutrients": "",
            "tillage": "",
            "crop_suitability": {},
            "recommendations": [],
            "improvements": [],
        }

        # Fertility assessment
        fertility_score = 0
        if 6.0 <= ph_water <= 7.5:
            fertility_score += 2
        elif 5.5 <= ph_water <= 8.0:
            fertility_score += 1

        if organic_carbon > 15:
            fertility_score += 2
        elif organic_carbon > 10:
            fertility_score += 1

        if cation_exchange > 15:
            fertility_score += 2
        elif cation_exchange > 10:
            fertility_score += 1

        if fertility_score >= 5:
            insights["fertility"] = "High - Excellent soil fertility"
        elif fertility_score >= 3:
            insights["fertility"] = "Moderate - Good soil fertility"
        else:
            insights["fertility"] = "Low - Soil fertility needs improvement"

        # Drainage assessment
        if sand_content > 60:
            insights[
                "drainage"
            ] = "Excellent - Well-drained, may need frequent irrigation"
        elif sand_content > 40:
            insights["drainage"] = "Good - Well-drained soil"
        elif clay_content > 40:
            insights["drainage"] = "Poor - May have drainage issues"
        else:
            insights["drainage"] = "Moderate - Adequate drainage"

        # Water retention
        if clay_content > 30:
            insights["water_retention"] = "High - Good water holding capacity"
        elif silt_content > 40:
            insights["water_retention"] = "Moderate - Fair water retention"
        else:
            insights["water_retention"] = "Low - Requires frequent irrigation"

        # Nutrient availability
        if ph_water < 5.5:
            insights[
                "nutrients"
            ] = "Limited - Acidic conditions may reduce availability"
        elif ph_water > 8.0:
            insights[
                "nutrients"
            ] = "Limited - Alkaline conditions may cause deficiencies"
        else:
            insights["nutrients"] = "Good - Favorable for nutrient availability"

        # Tillage requirements
        if bulk_density > 1.6:
            insights["tillage"] = "Deep tillage needed - Soil compaction present"
        elif clay_content > 40:
            insights["tillage"] = "Careful timing required - Heavy soil"
        else:
            insights["tillage"] = "Standard tillage suitable"

        # Crop suitability
        insights["crop_suitability"] = self._assess_crop_suitability(
            ph_water, organic_carbon, clay_content, sand_content, silt_content
        )

        # Management recommendations
        if ph_water < 6.0:
            insights["recommendations"].append("Apply lime to increase soil pH")
        if ph_water > 8.0:
            insights["recommendations"].append(
                "Apply sulfur or organic matter to reduce pH"
            )
        if organic_carbon < 10:
            insights["recommendations"].append("Add compost or organic matter")
        if bulk_density > 1.6:
            insights["recommendations"].append(
                "Implement deep tillage and avoid traffic on wet soil"
            )
        if sand_content > 70:
            insights["recommendations"].append(
                "Use frequent, light irrigation and organic mulch"
            )
        if clay_content > 50:
            insights["recommendations"].append(
                "Improve drainage and add organic matter"
            )

        # Improvement strategies
        if fertility_score < 3:
            insights["improvements"].append(
                "Implement comprehensive soil fertility program"
            )
        if organic_carbon < 15:
            insights["improvements"].append(
                "Establish cover cropping and composting program"
            )
        if cation_exchange < 10:
            insights["improvements"].append(
                "Add clay minerals or organic matter to improve CEC"
            )

        return insights

    def _assess_crop_suitability(
        self,
        ph_water: float,
        organic_carbon: float,
        clay_content: float,
        sand_content: float,
        silt_content: float,
    ) -> Dict[str, str]:
        """Assess suitability for different crop types."""

        suitability = {}

        # Rice suitability
        if clay_content > 30 and 5.5 <= ph_water <= 7.0:
            suitability["rice"] = "Excellent - Ideal conditions for rice cultivation"
        elif clay_content > 20:
            suitability["rice"] = "Good - Suitable for rice with proper management"
        else:
            suitability["rice"] = "Poor - Sandy soils not ideal for rice"

        # Wheat suitability
        if 6.0 <= ph_water <= 7.5 and 20 <= clay_content <= 40:
            suitability["wheat"] = "Excellent - Optimal conditions for wheat"
        elif 5.5 <= ph_water <= 8.0:
            suitability["wheat"] = "Good - Suitable for wheat cultivation"
        else:
            suitability["wheat"] = "Fair - May need soil amendments"

        # Cotton suitability
        if 5.8 <= ph_water <= 8.0 and clay_content > 20:
            suitability["cotton"] = "Good - Suitable for cotton cultivation"
        elif sand_content > 60:
            suitability["cotton"] = "Fair - Sandy soils need careful management"
        else:
            suitability["cotton"] = "Moderate - Adequate for cotton"

        # Vegetable crops
        if 6.0 <= ph_water <= 7.0 and organic_carbon > 15:
            suitability["vegetables"] = "Excellent - Ideal for vegetable production"
        elif 5.5 <= ph_water <= 7.5:
            suitability["vegetables"] = "Good - Suitable for most vegetables"
        else:
            suitability["vegetables"] = "Fair - May need soil improvement"

        # Legumes
        if 6.0 <= ph_water <= 7.5:
            suitability["legumes"] = "Good - Suitable for legume cultivation"
        elif ph_water < 5.5:
            suitability["legumes"] = "Poor - Too acidic for most legumes"
        else:
            suitability["legumes"] = "Fair - Acceptable with management"

        return suitability
