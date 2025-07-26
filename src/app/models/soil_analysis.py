from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..config.database import Base


class SoilAnalysis(Base):
    """Soil analysis model for storing user location soil data."""

    __tablename__ = "soil_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Location Information
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_name = Column(String)  # Optional human-readable location

    # Soil Analysis Results
    raw_data = Column(JSON)  # Complete SoilGrids API response
    summary = Column(Text)  # Human-readable summary

    # Key Soil Properties (extracted for easy querying)
    ph_value = Column(Float)  # pH in water (0-30cm)
    ph_description = Column(String)  # acidic, neutral, alkaline

    organic_carbon = Column(Float)  # Soil organic carbon (g/kg)
    organic_carbon_description = Column(String)  # low, moderate, high

    clay_percentage = Column(Float)  # Clay content (%)
    sand_percentage = Column(Float)  # Sand content (%)
    silt_percentage = Column(Float)  # Silt content (%)
    soil_texture = Column(String)  # Derived soil texture class

    nitrogen_content = Column(Float)  # Nitrogen content
    bulk_density = Column(Float)  # Bulk density
    cation_exchange_capacity = Column(Float)  # CEC

    # Analysis Status
    analysis_status = Column(String, default="completed")  # pending, completed, failed
    analysis_date = Column(DateTime, default=func.now())

    # Quality and Recommendations
    soil_quality_score = Column(Float)  # 0-100 overall soil quality score
    recommendations = Column(Text)  # Agricultural recommendations
    suitable_crops = Column(JSON)  # List of recommended crops

    # Metadata
    data_source = Column(String, default="SoilGrids_v2.0")
    api_version = Column(String, default="2.0")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="soil_analyses")

    def calculate_soil_quality_score(self) -> float:
        """
        Calculate an overall soil quality score based on key parameters.

        Returns:
            float: Soil quality score (0-100)
        """
        score = 0.0
        factors = 0

        # pH score (optimal range 6.0-7.5)
        if self.ph_value:
            if 6.0 <= self.ph_value <= 7.5:
                ph_score = 100
            elif 5.5 <= self.ph_value < 6.0 or 7.5 < self.ph_value <= 8.0:
                ph_score = 80
            elif 5.0 <= self.ph_value < 5.5 or 8.0 < self.ph_value <= 8.5:
                ph_score = 60
            else:
                ph_score = 40
            score += ph_score
            factors += 1

        # Organic carbon score (higher is better)
        if self.organic_carbon:
            if self.organic_carbon >= 30:
                oc_score = 100
            elif self.organic_carbon >= 20:
                oc_score = 80
            elif self.organic_carbon >= 10:
                oc_score = 60
            else:
                oc_score = 40
            score += oc_score
            factors += 1

        # Texture balance score (loam is ideal)
        if all([self.clay_percentage, self.sand_percentage, self.silt_percentage]):
            # Ideal ranges: Clay 20-30%, Sand 30-50%, Silt 30-50%
            clay_score = max(0, 100 - abs(self.clay_percentage - 25) * 4)
            sand_score = max(0, 100 - abs(self.sand_percentage - 40) * 2)
            silt_score = max(0, 100 - abs(self.silt_percentage - 35) * 2)
            texture_score = (clay_score + sand_score + silt_score) / 3
            score += texture_score
            factors += 1

        return score / factors if factors > 0 else 0.0

    def generate_recommendations(self) -> str:
        """
        Generate agricultural recommendations based on soil analysis.

        Returns:
            str: Recommendations text
        """
        recommendations = []

        # pH recommendations
        if self.ph_value:
            if self.ph_value < 6.0:
                recommendations.append(
                    "Consider lime application to raise soil pH for better nutrient availability."
                )
            elif self.ph_value > 7.5:
                recommendations.append(
                    "Consider sulfur application or organic matter to lower soil pH."
                )

        # Organic carbon recommendations
        if self.organic_carbon and self.organic_carbon < 15:
            recommendations.append(
                "Increase organic matter through compost, cover crops, or organic fertilizers."
            )

        # Texture recommendations
        if self.clay_percentage and self.clay_percentage > 40:
            recommendations.append(
                "Heavy clay soil - improve drainage and add organic matter for better structure."
            )
        elif self.sand_percentage and self.sand_percentage > 70:
            recommendations.append(
                "Sandy soil - add organic matter to improve water and nutrient retention."
            )

        return (
            " ".join(recommendations)
            if recommendations
            else "Soil conditions are generally suitable for agriculture."
        )

    def get_suitable_crops(self) -> list:
        """
        Suggest suitable crops based on soil properties.

        Returns:
            list: List of suitable crop names
        """
        suitable_crops = []

        if not self.ph_value:
            return ["Rice", "Wheat", "Maize"]  # Default crops

        # pH-based crop recommendations
        if 5.5 <= self.ph_value <= 6.5:
            suitable_crops.extend(["Rice", "Tea", "Coffee", "Potato"])
        elif 6.0 <= self.ph_value <= 7.5:
            suitable_crops.extend(["Wheat", "Maize", "Soybean", "Cotton", "Tomato"])
        elif 7.0 <= self.ph_value <= 8.0:
            suitable_crops.extend(["Barley", "Sugar Beet", "Cabbage"])

        # Organic carbon considerations
        if self.organic_carbon and self.organic_carbon > 20:
            suitable_crops.extend(["Vegetables", "Fruits", "Cash Crops"])

        # Remove duplicates and return top 5
        return list(set(suitable_crops))[:5]
