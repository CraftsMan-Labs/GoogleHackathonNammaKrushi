"""
Weather Analysis MCP Tools

Provides weather data and agricultural forecasts through the MCP interface.
Integrates with existing NammaKrushi weather services.
"""

import logging
from typing import Dict, Any, Optional
from ..tools.weather import get_weather_by_location, get_weather_by_coordinates
from ..security.zero_retention import get_zero_retention_proxy

logger = logging.getLogger(__name__)


class WeatherAnalysisTool:
    """
    MCP tool for weather analysis and agricultural forecasting.

    Provides current weather data, forecasts, and agricultural recommendations
    while maintaining zero data retention.
    """

    def __init__(self):
        self.zero_retention_proxy = get_zero_retention_proxy()

    async def analyze(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze weather conditions for agricultural planning.

        Args:
            args: Sanitized arguments containing:
                - location: Location name (required)
                - latitude: Latitude coordinate (optional)
                - longitude: Longitude coordinate (optional)

        Returns:
            Weather analysis with agricultural recommendations
        """
        try:
            # Extract parameters
            location = args.get("location", "").strip()
            latitude = args.get("latitude")
            longitude = args.get("longitude")

            if not location and (latitude is None or longitude is None):
                return {
                    "error": "missing_location_data",
                    "message": "Either location name or coordinates (latitude, longitude) are required",
                }

            # Sanitize location to city level
            if location:
                location = self.zero_retention_proxy.sanitize_location(location)

            # Get weather data
            weather_data = None

            if latitude is not None and longitude is not None:
                # Use coordinates for more precise data
                weather_data = await get_weather_by_coordinates(latitude, longitude)
            elif location:
                # Use location name
                weather_data = await get_weather_by_location(location)

            if not weather_data or weather_data.get("status") != "success":
                return {
                    "error": "weather_data_unavailable",
                    "message": "Unable to retrieve weather data for the specified location",
                }

            # Format weather analysis for agricultural use
            formatted_result = self._format_weather_analysis(weather_data, location)

            logger.info(f"Weather analysis completed for location: {location}")
            return formatted_result

        except Exception as e:
            logger.error(f"Error in weather analysis: {e}")
            return {
                "error": "weather_analysis_failed",
                "message": "Unable to complete weather analysis. Please try again.",
                "details": str(e) if logger.isEnabledFor(logging.DEBUG) else None,
            }

    def _format_weather_analysis(
        self, weather_data: Dict[str, Any], location: str
    ) -> Dict[str, Any]:
        """
        Format weather data for agricultural analysis.

        Args:
            weather_data: Raw weather data from service
            location: Sanitized location name

        Returns:
            Formatted weather analysis with agricultural insights
        """
        try:
            data = weather_data.get("data", {})

            # Extract current conditions
            current = data.get("current", {})
            temp_c = current.get("temp_c", 0)
            humidity = current.get("humidity", 0)
            wind_kph = current.get("wind_kph", 0)
            pressure_mb = current.get("pressure_mb", 0)
            uv = current.get("uv", 0)
            condition = current.get("condition", {}).get("text", "Unknown")

            # Extract forecast data if available
            forecast = data.get("forecast", {}).get("forecastday", [])

            # Generate agricultural recommendations
            agricultural_insights = self._generate_agricultural_insights(
                temp_c, humidity, wind_kph, pressure_mb, uv, condition, forecast
            )

            formatted_result = {
                "status": "success",
                "location": location,
                "current_conditions": {
                    "temperature_celsius": temp_c,
                    "temperature_fahrenheit": round(temp_c * 9 / 5 + 32, 1),
                    "humidity_percent": humidity,
                    "wind_speed_kph": wind_kph,
                    "pressure_mb": pressure_mb,
                    "uv_index": uv,
                    "condition": condition,
                    "timestamp": current.get("last_updated", ""),
                },
                "agricultural_assessment": {
                    "irrigation_recommendation": agricultural_insights["irrigation"],
                    "field_work_suitability": agricultural_insights["field_work"],
                    "disease_risk_level": agricultural_insights["disease_risk"],
                    "pest_activity_risk": agricultural_insights["pest_risk"],
                    "crop_stress_indicators": agricultural_insights["crop_stress"],
                },
                "farming_recommendations": agricultural_insights["recommendations"],
                "weather_alerts": agricultural_insights["alerts"],
            }

            # Add forecast if available
            if forecast:
                formatted_result["forecast"] = self._format_forecast_for_agriculture(
                    forecast[:3]
                )

            return formatted_result

        except Exception as e:
            logger.error(f"Error formatting weather analysis: {e}")
            return {
                "error": "formatting_failed",
                "message": "Weather data retrieved but formatting failed",
                "raw_data": weather_data,
            }

    def _generate_agricultural_insights(
        self,
        temp_c: float,
        humidity: int,
        wind_kph: float,
        pressure_mb: float,
        uv: float,
        condition: str,
        forecast: list,
    ) -> Dict[str, Any]:
        """
        Generate agricultural insights from weather data.

        Args:
            temp_c: Temperature in Celsius
            humidity: Humidity percentage
            wind_kph: Wind speed in km/h
            pressure_mb: Atmospheric pressure in mb
            uv: UV index
            condition: Weather condition description
            forecast: Forecast data

        Returns:
            Agricultural insights and recommendations
        """
        insights = {
            "irrigation": "",
            "field_work": "",
            "disease_risk": "",
            "pest_risk": "",
            "crop_stress": [],
            "recommendations": [],
            "alerts": [],
        }

        # Irrigation recommendations
        if humidity < 40:
            insights[
                "irrigation"
            ] = "High - Low humidity indicates increased water needs"
        elif humidity > 80:
            insights[
                "irrigation"
            ] = "Low - High humidity reduces irrigation requirements"
        else:
            insights["irrigation"] = "Moderate - Monitor soil moisture levels"

        # Field work suitability
        if "rain" in condition.lower() or "storm" in condition.lower():
            insights[
                "field_work"
            ] = "Not suitable - Wet conditions prevent field operations"
        elif wind_kph > 25:
            insights[
                "field_work"
            ] = "Limited - High winds may affect spraying and harvesting"
        elif temp_c > 35:
            insights["field_work"] = "Early morning/evening only - Avoid midday heat"
        else:
            insights["field_work"] = "Suitable - Good conditions for field operations"

        # Disease risk assessment
        if humidity > 75 and 20 <= temp_c <= 30:
            insights[
                "disease_risk"
            ] = "High - Warm, humid conditions favor fungal diseases"
        elif humidity > 60 and temp_c > 25:
            insights["disease_risk"] = "Moderate - Monitor crops for disease symptoms"
        else:
            insights[
                "disease_risk"
            ] = "Low - Current conditions less favorable for diseases"

        # Pest activity risk
        if temp_c > 25 and humidity > 60:
            insights[
                "pest_risk"
            ] = "High - Warm, humid conditions increase pest activity"
        elif temp_c > 30:
            insights["pest_risk"] = "Moderate - Heat stress may attract certain pests"
        else:
            insights["pest_risk"] = "Low - Current conditions less favorable for pests"

        # Crop stress indicators
        if temp_c > 35:
            insights["crop_stress"].append(
                "Heat stress - Provide shade or increase irrigation"
            )
        if temp_c < 10:
            insights["crop_stress"].append("Cold stress - Protect sensitive crops")
        if humidity < 30:
            insights["crop_stress"].append(
                "Drought stress - Increase irrigation frequency"
            )
        if wind_kph > 30:
            insights["crop_stress"].append(
                "Wind stress - Provide windbreaks for young plants"
            )

        # General recommendations
        if temp_c > 30 and humidity < 50:
            insights["recommendations"].append(
                "Increase irrigation frequency and consider mulching"
            )
        if humidity > 80:
            insights["recommendations"].append(
                "Improve field drainage and air circulation"
            )
        if uv > 8:
            insights["recommendations"].append(
                "Protect workers and sensitive crops from UV exposure"
            )
        if "rain" in condition.lower():
            insights["recommendations"].append(
                "Postpone spraying operations and harvest activities"
            )

        # Weather alerts
        if temp_c > 40:
            insights["alerts"].append(
                "Extreme heat warning - Take immediate protective measures"
            )
        if wind_kph > 40:
            insights["alerts"].append(
                "High wind warning - Secure equipment and structures"
            )
        if humidity > 90:
            insights["alerts"].append("Very high humidity - Increased disease risk")

        return insights

    def _format_forecast_for_agriculture(self, forecast_days: list) -> list:
        """
        Format forecast data for agricultural planning.

        Args:
            forecast_days: List of forecast day data

        Returns:
            Formatted forecast with agricultural focus
        """
        formatted_forecast = []

        for day_data in forecast_days:
            day = day_data.get("day", {})
            date = day_data.get("date", "")

            # Extract key agricultural metrics
            max_temp = day.get("maxtemp_c", 0)
            min_temp = day.get("mintemp_c", 0)
            avg_humidity = day.get("avghumidity", 0)
            max_wind = day.get("maxwind_kph", 0)
            total_precip = day.get("totalprecip_mm", 0)
            condition = day.get("condition", {}).get("text", "Unknown")

            # Generate daily agricultural assessment
            daily_assessment = {
                "date": date,
                "temperature_range": f"{min_temp}°C - {max_temp}°C",
                "precipitation_mm": total_precip,
                "avg_humidity": avg_humidity,
                "max_wind_kph": max_wind,
                "condition": condition,
                "agricultural_suitability": self._assess_daily_suitability(
                    max_temp, min_temp, avg_humidity, max_wind, total_precip, condition
                ),
            }

            formatted_forecast.append(daily_assessment)

        return formatted_forecast

    def _assess_daily_suitability(
        self,
        max_temp: float,
        min_temp: float,
        avg_humidity: int,
        max_wind: float,
        total_precip: float,
        condition: str,
    ) -> Dict[str, str]:
        """
        Assess daily weather suitability for various agricultural activities.

        Returns:
            Assessment for different agricultural activities
        """
        assessment = {}

        # Irrigation needs
        if total_precip > 10:
            assessment["irrigation"] = "Not needed - Adequate rainfall expected"
        elif avg_humidity < 40 or max_temp > 35:
            assessment["irrigation"] = "High priority - Hot/dry conditions"
        else:
            assessment["irrigation"] = "Monitor - Check soil moisture"

        # Spraying suitability
        if total_precip > 5 or max_wind > 15:
            assessment["spraying"] = "Not suitable - Rain or wind expected"
        else:
            assessment["spraying"] = "Suitable - Good conditions for application"

        # Harvesting suitability
        if total_precip > 2:
            assessment["harvesting"] = "Not suitable - Wet conditions"
        elif max_wind > 25:
            assessment["harvesting"] = "Limited - High winds may cause issues"
        else:
            assessment["harvesting"] = "Suitable - Good conditions for harvest"

        # Planting suitability
        if 15 <= min_temp <= 25 and 20 <= max_temp <= 30 and total_precip < 20:
            assessment["planting"] = "Excellent - Ideal conditions for planting"
        elif total_precip > 25:
            assessment["planting"] = "Poor - Too wet for planting"
        else:
            assessment["planting"] = "Fair - Acceptable conditions"

        return assessment
