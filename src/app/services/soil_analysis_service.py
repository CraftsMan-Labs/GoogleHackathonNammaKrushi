"""
Soil Analysis Service

Enhanced service for processing and storing soil analysis data during user registration.
"""

import json
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from ..models.soil_analysis import SoilAnalysis
from ..tools.soil_analysis import get_soilgrids_data


class SoilAnalysisService:
    """Service for handling soil analysis operations."""

    def __init__(self, db: Session):
        self.db = db

    async def analyze_and_store_soil_data(
        self,
        user_id: int,
        latitude: float,
        longitude: float,
        location_name: Optional[str] = None,
    ) -> SoilAnalysis:
        """
        Fetch soil data from SoilGrids API and store analysis in database.

        Args:
            user_id (int): User ID
            latitude (float): Latitude coordinate
            longitude (float): Longitude coordinate
            location_name (str, optional): Human-readable location name

        Returns:
            SoilAnalysis: Created soil analysis record
        """
        try:
            # Fetch soil data from SoilGrids API
            logging.info(f"Fetching soil data for coordinates: {latitude}, {longitude}")
            soil_data_response = await get_soilgrids_data(latitude, longitude)

            if soil_data_response["status"] != "success":
                raise Exception(
                    f"Soil data fetch failed: {soil_data_response.get('error_message', 'Unknown error')}"
                )

            # Parse the raw soil data
            raw_data = json.loads(soil_data_response["data"])
            summary = soil_data_response.get("summary", "")
            data_source = soil_data_response.get("data_source", "SoilGrids_v2.0")

            # Extract key soil properties
            soil_properties = self._extract_soil_properties(raw_data)
            # Create soil analysis record
            soil_analysis = SoilAnalysis(
                user_id=user_id,
                latitude=latitude,
                longitude=longitude,
                location_name=location_name,
                raw_data=raw_data,
                summary=summary,
                **soil_properties,
                analysis_status="completed",
                data_source=data_source,
                api_version="2.0",
            )

            # Calculate soil quality score
            soil_analysis.soil_quality_score = (
                soil_analysis.calculate_soil_quality_score()
            )

            # Generate recommendations
            soil_analysis.recommendations = soil_analysis.generate_recommendations()

            # Get suitable crops
            soil_analysis.suitable_crops = soil_analysis.get_suitable_crops()

            # Save to database
            self.db.add(soil_analysis)
            self.db.commit()
            self.db.refresh(soil_analysis)

            logging.info(
                f"Soil analysis completed for user {user_id} with quality score: {soil_analysis.soil_quality_score:.1f}"
            )

            return soil_analysis

        except Exception as e:
            logging.error(f"Soil analysis failed for user {user_id}: {str(e)}")

            # Create failed analysis record
            failed_analysis = SoilAnalysis(
                user_id=user_id,
                latitude=latitude,
                longitude=longitude,
                location_name=location_name,
                analysis_status="failed",
                summary=f"Analysis failed: {str(e)}",
                data_source="SoilGrids_v2.0",
            )

            self.db.add(failed_analysis)
            self.db.commit()
            self.db.refresh(failed_analysis)

            return failed_analysis

    def _extract_soil_properties(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key soil properties from raw SoilGrids data.

        Args:
            raw_data (Dict[str, Any]): Raw soil data from SoilGrids API

        Returns:
            Dict[str, Any]: Extracted soil properties
        """
        properties = {}

        try:
            # Extract pH (0-30cm layer)
            if "phh2o" in raw_data and "0-30cm" in raw_data["phh2o"]:
                ph_raw = raw_data["phh2o"]["0-30cm"].get("mean")
                if ph_raw is not None and ph_raw > 0:
                    properties["ph_value"] = ph_raw / 10  # Convert from pH*10

                    if properties["ph_value"] < 6.0:
                        properties["ph_description"] = "acidic"
                    elif properties["ph_value"] > 7.5:
                        properties["ph_description"] = "alkaline"
                    else:
                        properties["ph_description"] = "neutral"
            # Extract organic carbon (0-30cm layer)
            if "soc" in raw_data and "0-30cm" in raw_data["soc"]:
                soc_raw = raw_data["soc"]["0-30cm"].get("mean")
                if soc_raw is not None and soc_raw > 0:
                    properties["organic_carbon"] = soc_raw / 10  # Convert from g/kg*10

                    if properties["organic_carbon"] < 10:
                        properties["organic_carbon_description"] = "low"
                    elif properties["organic_carbon"] > 30:
                        properties["organic_carbon_description"] = "high"
                    else:
                        properties["organic_carbon_description"] = "moderate"
            # Extract soil texture (0-30cm layer)
            texture_components = {}
            for component in ["clay", "sand", "silt"]:
                if component in raw_data and "0-30cm" in raw_data[component]:
                    value_raw = raw_data[component]["0-30cm"].get("mean")
                    if value_raw is not None and value_raw > 0:
                        value = value_raw / 10  # Convert from %*10
                        properties[f"{component}_percentage"] = value
                        texture_components[component] = value

            # Determine soil texture class
            if texture_components:
                properties["soil_texture"] = self._determine_soil_texture(
                    texture_components
                )

            # Extract other properties
            if "nitrogen" in raw_data and "0-30cm" in raw_data["nitrogen"]:
                nitrogen_raw = raw_data["nitrogen"]["0-30cm"].get("mean")
                if nitrogen_raw is not None:
                    properties["nitrogen_content"] = nitrogen_raw / 100

            if "bdod" in raw_data and "0-30cm" in raw_data["bdod"]:
                bdod_raw = raw_data["bdod"]["0-30cm"].get("mean")
                if bdod_raw is not None:
                    properties["bulk_density"] = bdod_raw / 100

            if "cec" in raw_data and "0-30cm" in raw_data["cec"]:
                cec_raw = raw_data["cec"]["0-30cm"].get("mean")
                if cec_raw is not None:
                    properties["cation_exchange_capacity"] = cec_raw / 10

        except Exception as e:
            logging.error(f"Error extracting soil properties: {str(e)}")

        return properties

    def _determine_soil_texture(self, components: Dict[str, float]) -> str:
        """
        Determine soil texture class based on clay, sand, and silt percentages.

        Args:
            components (Dict[str, float]): Texture components with percentages

        Returns:
            str: Soil texture class
        """
        clay = components.get("clay", 0)
        sand = components.get("sand", 0)
        silt = components.get("silt", 0)

        # Simplified texture classification
        if clay >= 40:
            return "Clay"
        elif clay >= 27 and sand <= 45:
            return "Clay Loam"
        elif clay >= 20 and sand >= 45:
            return "Sandy Clay Loam"
        elif clay < 20 and sand >= 70:
            return "Sandy Loam" if silt >= 15 else "Sand"
        elif clay < 20 and sand < 50 and silt >= 50:
            return "Silt Loam"
        elif clay < 20 and sand < 70 and silt < 50:
            return "Loam"
        else:
            return "Mixed"

    def get_user_soil_analyses(self, user_id: int) -> list[SoilAnalysis]:
        """
        Get all soil analyses for a user.

        Args:
            user_id (int): User ID

        Returns:
            list[SoilAnalysis]: List of soil analyses
        """
        return (
            self.db.query(SoilAnalysis)
            .filter(SoilAnalysis.user_id == user_id)
            .order_by(SoilAnalysis.created_at.desc())
            .all()
        )

    def get_latest_soil_analysis(self, user_id: int) -> Optional[SoilAnalysis]:
        """
        Get the latest soil analysis for a user.

        Args:
            user_id (int): User ID

        Returns:
            Optional[SoilAnalysis]: Latest soil analysis or None
        """
        return (
            self.db.query(SoilAnalysis)
            .filter(SoilAnalysis.user_id == user_id)
            .order_by(SoilAnalysis.created_at.desc())
            .first()
        )
