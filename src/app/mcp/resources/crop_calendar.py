"""
Crop Calendar MCP Resource

Provides seasonal crop planting and harvesting calendar data for Karnataka
through the MCP interface.
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CropCalendarResource:
    """
    MCP resource for Karnataka crop calendar information.

    Provides seasonal planting and harvesting schedules, optimal timing,
    and crop-specific recommendations for Karnataka farmers.
    """

    def __init__(self):
        self.calendar_data = self._initialize_crop_calendar()

    async def get_calendar(self) -> Dict[str, Any]:
        """
        Get the complete crop calendar for Karnataka.

        Returns:
            Comprehensive crop calendar with seasonal information
        """
        try:
            current_month = datetime.now().month
            current_season = self._get_current_season(current_month)

            calendar_response = {
                "status": "success",
                "region": "Karnataka, India",
                "current_season": current_season,
                "current_month_recommendations": self._get_current_month_activities(
                    current_month
                ),
                "seasons": self.calendar_data["seasons"],
                "crops": self.calendar_data["crops"],
                "monthly_activities": self.calendar_data["monthly_activities"],
                "weather_considerations": self.calendar_data["weather_considerations"],
                "general_guidelines": self.calendar_data["general_guidelines"],
            }

            logger.info("Crop calendar data retrieved successfully")
            return calendar_response

        except Exception as e:
            logger.error(f"Error retrieving crop calendar: {e}")
            return {
                "error": "calendar_retrieval_failed",
                "message": "Unable to retrieve crop calendar data",
            }

    def _initialize_crop_calendar(self) -> Dict[str, Any]:
        """Initialize the Karnataka crop calendar data."""
        return {
            "seasons": {
                "kharif": {
                    "name": "Kharif (Monsoon Season)",
                    "period": "June - October",
                    "months": [6, 7, 8, 9, 10],
                    "description": "Monsoon-dependent crops grown during rainy season",
                    "characteristics": [
                        "High rainfall and humidity",
                        "Warm temperatures",
                        "Good for water-intensive crops",
                        "Risk of flooding and waterlogging",
                    ],
                    "major_crops": ["Rice", "Cotton", "Sugarcane", "Maize", "Pulses"],
                },
                "rabi": {
                    "name": "Rabi (Winter Season)",
                    "period": "November - March",
                    "months": [11, 12, 1, 2, 3],
                    "description": "Winter crops grown with irrigation support",
                    "characteristics": [
                        "Cool and dry weather",
                        "Requires irrigation",
                        "Lower pest and disease pressure",
                        "Good for quality crop production",
                    ],
                    "major_crops": ["Wheat", "Barley", "Gram", "Mustard", "Vegetables"],
                },
                "summer": {
                    "name": "Summer (Zaid Season)",
                    "period": "April - June",
                    "months": [4, 5, 6],
                    "description": "Summer crops with intensive irrigation",
                    "characteristics": [
                        "Hot and dry conditions",
                        "High irrigation requirements",
                        "Shorter growing season",
                        "Heat-tolerant crops preferred",
                    ],
                    "major_crops": [
                        "Fodder crops",
                        "Vegetables",
                        "Watermelon",
                        "Cucumber",
                    ],
                },
            },
            "crops": {
                "rice": {
                    "season": "Kharif",
                    "planting_months": [6, 7],
                    "harvesting_months": [10, 11],
                    "duration_days": 120,
                    "water_requirement": "High",
                    "soil_type": "Clay, Clay loam",
                    "varieties": {
                        "short_duration": ["BPT 5204", "KMP 1", "Intan"],
                        "medium_duration": ["IR 64", "Jaya", "Rasi"],
                        "long_duration": ["Mugad Sugandha", "Dodiga"],
                    },
                    "key_activities": {
                        "june": "Land preparation, nursery sowing",
                        "july": "Transplanting",
                        "august": "Weeding, fertilizer application",
                        "september": "Pest monitoring, water management",
                        "october": "Harvesting preparation",
                        "november": "Harvesting",
                    },
                },
                "cotton": {
                    "season": "Kharif",
                    "planting_months": [6, 7],
                    "harvesting_months": [12, 1, 2],
                    "duration_days": 180,
                    "water_requirement": "Medium",
                    "soil_type": "Black cotton soil, Red soil",
                    "varieties": {
                        "hybrid": ["Bunny Bt", "RCH 2", "MRC 7017"],
                        "desi": ["Jayadhar", "Surabhi"],
                    },
                    "key_activities": {
                        "june": "Land preparation, seed treatment",
                        "july": "Sowing",
                        "august": "Gap filling, weeding",
                        "september": "Pest control, fertilizer application",
                        "october": "Flowering stage management",
                        "november": "Boll development monitoring",
                        "december": "First picking",
                        "january": "Second picking",
                        "february": "Final picking",
                    },
                },
                "wheat": {
                    "season": "Rabi",
                    "planting_months": [11, 12],
                    "harvesting_months": [3, 4],
                    "duration_days": 120,
                    "water_requirement": "Medium",
                    "soil_type": "Loam, Clay loam",
                    "varieties": {
                        "irrigated": ["HD 2967", "PBW 343", "WH 1105"],
                        "rainfed": ["HI 1544", "NIAW 34"],
                    },
                    "key_activities": {
                        "november": "Land preparation, sowing",
                        "december": "Irrigation, weed control",
                        "january": "Fertilizer application",
                        "february": "Pest monitoring, irrigation",
                        "march": "Grain filling stage",
                        "april": "Harvesting",
                    },
                },
                "maize": {
                    "season": "Kharif/Rabi",
                    "planting_months": [6, 7, 11, 12],
                    "harvesting_months": [9, 10, 3, 4],
                    "duration_days": 90,
                    "water_requirement": "Medium",
                    "soil_type": "Well-drained loam",
                    "varieties": {
                        "kharif": ["Ganga 5", "Deccan 107", "NAC 6002"],
                        "rabi": ["Ganga 2", "Vijay", "Surya"],
                    },
                    "key_activities": {
                        "kharif": {
                            "june": "Land preparation, sowing",
                            "july": "Thinning, weeding",
                            "august": "Fertilizer application",
                            "september": "Pest control",
                            "october": "Harvesting",
                        },
                        "rabi": {
                            "november": "Land preparation, sowing",
                            "december": "Weeding, irrigation",
                            "january": "Fertilizer application",
                            "february": "Pest monitoring",
                            "march": "Harvesting",
                        },
                    },
                },
                "sugarcane": {
                    "season": "Annual",
                    "planting_months": [1, 2, 3, 10, 11, 12],
                    "harvesting_months": [12, 1, 2, 3, 4],
                    "duration_days": 365,
                    "water_requirement": "Very High",
                    "soil_type": "Deep, well-drained loam",
                    "varieties": {
                        "early": ["Co 86032", "Co 94012"],
                        "mid_late": ["Co 8371", "Co 94008"],
                    },
                    "key_activities": {
                        "planting_season": "Land preparation, planting",
                        "growing_season": "Regular irrigation, fertilization, pest control",
                        "harvest_season": "Harvesting, ratoon management",
                    },
                },
            },
            "monthly_activities": {
                1: {
                    "month": "January",
                    "season": "Rabi",
                    "activities": [
                        "Harvest cotton (second picking)",
                        "Irrigate wheat and other rabi crops",
                        "Plant sugarcane",
                        "Prepare land for summer crops",
                        "Pest monitoring in standing crops",
                    ],
                },
                2: {
                    "month": "February",
                    "season": "Rabi",
                    "activities": [
                        "Final cotton picking",
                        "Apply fertilizers to wheat",
                        "Continue sugarcane planting",
                        "Harvest early vegetables",
                        "Prepare for summer crop planning",
                    ],
                },
                3: {
                    "month": "March",
                    "season": "Rabi/Summer",
                    "activities": [
                        "Harvest wheat",
                        "Plant summer vegetables",
                        "Continue sugarcane operations",
                        "Prepare land for kharif crops",
                        "Repair irrigation systems",
                    ],
                },
                4: {
                    "month": "April",
                    "season": "Summer",
                    "activities": [
                        "Complete wheat harvest",
                        "Plant fodder crops",
                        "Summer vegetable management",
                        "Deep plowing for kharif preparation",
                        "Water conservation activities",
                    ],
                },
                5: {
                    "month": "May",
                    "season": "Summer",
                    "activities": [
                        "Summer crop management",
                        "Prepare nurseries for kharif crops",
                        "Repair farm equipment",
                        "Plan kharif crop selection",
                        "Soil testing and amendments",
                    ],
                },
                6: {
                    "month": "June",
                    "season": "Kharif",
                    "activities": [
                        "Sow rice, cotton, maize",
                        "Land preparation with monsoon",
                        "Transplant rice seedlings",
                        "Apply pre-emergence herbicides",
                        "Monitor weather for planting decisions",
                    ],
                },
                7: {
                    "month": "July",
                    "season": "Kharif",
                    "activities": [
                        "Complete kharif sowing",
                        "Transplant rice",
                        "Gap filling in cotton and maize",
                        "First weeding operations",
                        "Drainage management",
                    ],
                },
                8: {
                    "month": "August",
                    "season": "Kharif",
                    "activities": [
                        "Apply fertilizers to kharif crops",
                        "Second weeding",
                        "Pest and disease monitoring",
                        "Water management",
                        "Intercultural operations",
                    ],
                },
                9: {
                    "month": "September",
                    "season": "Kharif",
                    "activities": [
                        "Pest control in cotton",
                        "Flowering stage management",
                        "Harvest early maize",
                        "Prepare for post-monsoon activities",
                        "Disease management in rice",
                    ],
                },
                10: {
                    "month": "October",
                    "season": "Kharif/Rabi",
                    "activities": [
                        "Harvest rice",
                        "Cotton boll development monitoring",
                        "Prepare land for rabi crops",
                        "Plan rabi crop selection",
                        "Post-harvest management",
                    ],
                },
                11: {
                    "month": "November",
                    "season": "Rabi",
                    "activities": [
                        "Sow wheat and other rabi crops",
                        "Complete rice harvest",
                        "First cotton picking",
                        "Apply basal fertilizers",
                        "Irrigation scheduling",
                    ],
                },
                12: {
                    "month": "December",
                    "season": "Rabi",
                    "activities": [
                        "Continue cotton picking",
                        "Irrigate rabi crops",
                        "Weed control in wheat",
                        "Harvest sugarcane",
                        "Plan for next year's crops",
                    ],
                },
            },
            "weather_considerations": {
                "monsoon_management": [
                    "Ensure proper drainage in fields",
                    "Monitor for waterlogging",
                    "Adjust planting dates based on monsoon arrival",
                    "Use disease-resistant varieties during high humidity",
                ],
                "drought_management": [
                    "Select drought-tolerant varieties",
                    "Implement water conservation techniques",
                    "Use mulching to retain soil moisture",
                    "Plan contingency crops",
                ],
                "temperature_stress": [
                    "Provide shade for sensitive crops during extreme heat",
                    "Adjust irrigation frequency during hot weather",
                    "Use heat-tolerant varieties",
                    "Time field operations to avoid peak heat",
                ],
            },
            "general_guidelines": [
                "Always consider local weather patterns before planting",
                "Use certified seeds from reliable sources",
                "Follow integrated pest management practices",
                "Maintain proper crop rotation to preserve soil health",
                "Keep detailed records of farming activities",
                "Consult local agricultural extension officers",
                "Stay updated with weather forecasts and advisories",
                "Plan irrigation schedules based on crop requirements",
            ],
        }

    def _get_current_season(self, month: int) -> str:
        """Determine current season based on month."""
        if month in [6, 7, 8, 9, 10]:
            return "Kharif (Monsoon Season)"
        elif month in [11, 12, 1, 2, 3]:
            return "Rabi (Winter Season)"
        else:
            return "Summer (Zaid Season)"

    def _get_current_month_activities(self, month: int) -> Dict[str, Any]:
        """Get activities recommended for current month."""
        month_data = self.calendar_data["monthly_activities"].get(month, {})

        # Add specific crop activities for current month
        current_activities = {
            "general_activities": month_data.get("activities", []),
            "planting_opportunities": [],
            "harvesting_opportunities": [],
            "management_focus": [],
        }

        # Check which crops can be planted this month
        for crop_name, crop_data in self.calendar_data["crops"].items():
            if month in crop_data.get("planting_months", []):
                current_activities["planting_opportunities"].append(
                    {
                        "crop": crop_name.title(),
                        "season": crop_data.get("season", ""),
                        "duration": f"{crop_data.get('duration_days', 0)} days",
                    }
                )

            if month in crop_data.get("harvesting_months", []):
                current_activities["harvesting_opportunities"].append(
                    {"crop": crop_name.title(), "season": crop_data.get("season", "")}
                )

        # Add management focus based on season
        season = self._get_current_season(month)
        if "Kharif" in season:
            current_activities["management_focus"] = [
                "Monitor for pest and disease outbreaks",
                "Ensure proper drainage during heavy rains",
                "Apply fertilizers as per crop requirements",
                "Weed management in standing crops",
            ]
        elif "Rabi" in season:
            current_activities["management_focus"] = [
                "Irrigation scheduling and water management",
                "Cold protection for sensitive crops",
                "Fertilizer application for optimal growth",
                "Harvest planning and post-harvest management",
            ]
        else:  # Summer
            current_activities["management_focus"] = [
                "Water conservation and efficient irrigation",
                "Heat stress management",
                "Preparation for upcoming kharif season",
                "Equipment maintenance and repair",
            ]

        return current_activities
