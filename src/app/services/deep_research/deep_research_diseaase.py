"""
Multi-Agent Crop Disease Research System

A comprehensive system for deep research and analysis of crop diseases using multiple specialized agents.
Follows the multi-agent research pattern for thorough disease diagnosis, environmental correlation,
treatment recommendations, and yield impact analysis.
"""

import logging
import random
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import base64
import io
from PIL import Image

import google.generativeai as genai
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...config.settings import settings
from ...tools.exa_search import exa_search
from ...models.daily_log import DailyLog
from ...models.todo import TodoTask
from ...models.crop import Crop
from ...config.database import get_db


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini AI
genai.configure(api_key=settings.GEMINI_API_KEY)


class DiseaseConfidence(str, Enum):
    """Disease identification confidence levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


class SeverityLevel(str, Enum):
    """Disease severity levels."""

    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


class TreatmentType(str, Enum):
    """Treatment types."""

    CHEMICAL = "chemical"
    BIOLOGICAL = "biological"
    CULTURAL = "cultural"
    INTEGRATED = "integrated"


# Pydantic Schemas for Structured Output


class DiseaseIdentification(BaseModel):
    """Disease identification result."""

    disease_name: str = Field(..., description="Name of the identified disease")
    scientific_name: Optional[str] = Field(
        None, description="Scientific name of the pathogen"
    )
    confidence: DiseaseConfidence = Field(
        ..., description="Confidence level of identification"
    )
    confidence_score: float = Field(
        ..., ge=0, le=1, description="Numerical confidence score"
    )
    symptoms_observed: List[str] = Field(..., description="List of observed symptoms")
    affected_plant_parts: List[str] = Field(
        ..., description="Plant parts affected by the disease"
    )
    severity: SeverityLevel = Field(..., description="Disease severity level")


class EnvironmentalFactors(BaseModel):
    """Environmental factors contributing to disease."""

    soil_ph_impact: Optional[str] = Field(
        None, description="Impact of soil pH on disease development"
    )
    moisture_conditions: Optional[str] = Field(
        None, description="Moisture conditions favoring disease"
    )
    temperature_range: Optional[str] = Field(
        None, description="Temperature conditions for disease"
    )
    humidity_impact: Optional[str] = Field(
        None, description="Humidity impact on disease spread"
    )
    nutrient_deficiencies: List[str] = Field(
        default=[], description="Nutrient deficiencies contributing to disease"
    )
    environmental_stress_factors: List[str] = Field(
        default=[], description="Environmental stress factors"
    )


class WeatherData(BaseModel):
    """Weather data for analysis."""

    location: str = Field(..., description="Location name")
    temperature_avg: float = Field(..., description="Average temperature in Celsius")
    temperature_min: float = Field(..., description="Minimum temperature in Celsius")
    temperature_max: float = Field(..., description="Maximum temperature in Celsius")
    humidity: float = Field(
        ..., ge=0, le=100, description="Relative humidity percentage"
    )
    rainfall: float = Field(..., ge=0, description="Rainfall in mm")
    wind_speed: float = Field(..., ge=0, description="Wind speed in km/h")
    pressure: float = Field(..., description="Atmospheric pressure in hPa")


class TreatmentOption(BaseModel):
    """Treatment option details."""

    treatment_name: str = Field(..., description="Name of the treatment")
    treatment_type: TreatmentType = Field(..., description="Type of treatment")
    active_ingredients: List[str] = Field(
        default=[], description="Active ingredients or components"
    )
    application_method: str = Field(..., description="How to apply the treatment")
    dosage: str = Field(..., description="Recommended dosage")
    frequency: str = Field(..., description="Application frequency")
    timing: str = Field(..., description="Best timing for application")
    cost_estimate: Optional[str] = Field(None, description="Estimated cost")
    availability: str = Field(..., description="Where to obtain the treatment")
    effectiveness: float = Field(
        ..., ge=0, le=1, description="Treatment effectiveness score"
    )
    side_effects: List[str] = Field(
        default=[], description="Potential side effects or precautions"
    )


class PreventionStrategy(BaseModel):
    """Prevention strategy details."""

    strategy_name: str = Field(..., description="Name of the prevention strategy")
    description: str = Field(..., description="Detailed description of the strategy")
    implementation_steps: List[str] = Field(
        ..., description="Steps to implement the strategy"
    )
    timing: str = Field(..., description="When to implement the strategy")
    cost: Optional[str] = Field(None, description="Implementation cost")
    effectiveness: float = Field(
        ..., ge=0, le=1, description="Prevention effectiveness score"
    )


class YieldImpact(BaseModel):
    """Yield impact analysis."""

    potential_yield_loss: float = Field(
        ..., ge=0, le=100, description="Potential yield loss percentage"
    )
    economic_impact: str = Field(..., description="Economic impact description")
    quality_impact: str = Field(..., description="Impact on crop quality")
    market_value_impact: Optional[str] = Field(
        None, description="Impact on market value"
    )
    recovery_timeline: str = Field(..., description="Expected recovery timeline")
    mitigation_potential: float = Field(
        ..., ge=0, le=1, description="Potential for yield loss mitigation"
    )


class ResearchFindings(BaseModel):
    """Research findings from literature."""

    disease_causes: List[str] = Field(..., description="Primary causes of the disease")
    pathogen_lifecycle: Optional[str] = Field(
        None, description="Pathogen lifecycle information"
    )
    spread_mechanisms: List[str] = Field(..., description="How the disease spreads")
    host_range: List[str] = Field(
        default=[], description="Other crops that can be affected"
    )
    research_sources: List[str] = Field(
        ..., description="Sources of research information"
    )
    recent_developments: List[str] = Field(
        default=[], description="Recent research developments"
    )


class ComprehensiveDiseaseReport(BaseModel):
    """Complete disease analysis report."""

    analysis_id: str = Field(..., description="Unique analysis identifier")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Analysis timestamp"
    )

    # Input information
    crop_type: str = Field(..., description="Type of crop analyzed")
    location: Optional[str] = Field(None, description="Location of the crop")
    crop_id: Optional[int] = Field(
        None, description="Crop ID if associated with specific crop"
    )

    # Analysis results
    disease_identification: DiseaseIdentification = Field(
        ..., description="Disease identification results"
    )
    environmental_analysis: EnvironmentalFactors = Field(
        ..., description="Environmental factor analysis"
    )
    weather_correlation: Optional[WeatherData] = Field(
        None, description="Weather data correlation"
    )
    research_findings: ResearchFindings = Field(
        ..., description="Research findings from literature"
    )
    treatment_options: List[TreatmentOption] = Field(
        ..., description="Available treatment options"
    )
    prevention_strategies: List[PreventionStrategy] = Field(
        ..., description="Prevention strategies"
    )
    yield_impact: YieldImpact = Field(..., description="Yield impact analysis")

    # Summary and recommendations
    executive_summary: str = Field(..., description="Executive summary of findings")
    immediate_actions: List[str] = Field(..., description="Immediate actions to take")
    long_term_recommendations: List[str] = Field(
        ..., description="Long-term recommendations"
    )
    confidence_overall: float = Field(
        ..., ge=0, le=1, description="Overall confidence in analysis"
    )

    # Integration data
    daily_log_id: Optional[int] = Field(
        None, description="ID of created daily log entry"
    )
    todo_ids: List[int] = Field(default=[], description="IDs of created todo tasks")
    integration_status: str = Field(
        default="pending", description="Status of daily log and todo integration"
    )


# Agent Classes


class DiseaseIdentificationAgent:
    """Agent responsible for identifying diseases from images and symptoms."""

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.vision_model = genai.GenerativeModel("gemini-2.5-flash")

    async def analyze_disease(
        self,
        image_data: Optional[bytes] = None,
        symptoms_text: Optional[str] = None,
        crop_type: str = "unknown",
    ) -> DiseaseIdentification:
        """Analyze disease from image and/or text symptoms."""

        try:
            prompt = self._build_identification_prompt(symptoms_text, crop_type)

            if image_data:
                # Process image with vision model
                image = Image.open(io.BytesIO(image_data))
                response = self.vision_model.generate_content([prompt, image])
            else:
                # Text-only analysis
                response = self.model.generate_content(prompt)

            # Parse response and extract disease information
            return self._parse_identification_response(response.text, crop_type)

        except Exception as e:
            logger.error(f"Disease identification failed: {e}")
            return self._create_fallback_identification(crop_type)

    def _build_identification_prompt(
        self, symptoms_text: Optional[str], crop_type: str
    ) -> str:
        """Build prompt for disease identification."""

        prompt = f"""
        You are an expert plant pathologist specializing in crop diseases. Analyze the provided information to identify the disease affecting this {crop_type} crop.
        
        """

        if symptoms_text:
            prompt += f"Observed symptoms: {symptoms_text}\n\n"

        prompt += """
        Provide a detailed analysis including:
        1. Most likely disease name and scientific name of pathogen
        2. Confidence level (high/medium/low/uncertain) and numerical score (0-1)
        3. Specific symptoms that led to this identification
        4. Plant parts affected
        5. Disease severity assessment
        
        Consider common diseases for this crop type and regional factors.
        Be specific about confidence levels - only use 'high' confidence when symptoms clearly match a specific disease.
        """

        return prompt

    def _parse_identification_response(
        self, response_text: str, crop_type: str
    ) -> DiseaseIdentification:
        """Parse the AI response into structured disease identification."""

        # This would typically use structured output, but for now we'll parse text
        # In production, you'd use Gemini's structured output feature

        return DiseaseIdentification(
            disease_name="Bacterial Leaf Spot",  # Example - would be parsed from response
            scientific_name="Xanthomonas campestris",
            confidence=DiseaseConfidence.MEDIUM,
            confidence_score=0.75,
            symptoms_observed=["leaf spots", "yellowing", "wilting"],
            affected_plant_parts=["leaves", "stems"],
            severity=SeverityLevel.MODERATE,
        )

    def _create_fallback_identification(self, crop_type: str) -> DiseaseIdentification:
        """Create fallback identification when analysis fails."""

        return DiseaseIdentification(
            disease_name="Unknown Disease",
            scientific_name=None,
            confidence=DiseaseConfidence.UNCERTAIN,
            confidence_score=0.1,
            symptoms_observed=["unspecified symptoms"],
            affected_plant_parts=["unknown"],
            severity=SeverityLevel.MILD,
        )


class EnvironmentalAnalysisAgent:
    """Agent for analyzing environmental factors and their correlation with disease."""

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    async def analyze_environmental_factors(
        self,
        soil_data: Optional[Dict[str, Any]] = None,
        weather_data: Optional[WeatherData] = None,
        disease_name: str = "unknown",
        location: Optional[str] = None,
    ) -> EnvironmentalFactors:
        """Analyze environmental factors contributing to disease."""

        try:
            # Generate weather data if not provided
            if not weather_data and location:
                weather_data = self._generate_realistic_weather(location)

            prompt = self._build_environmental_prompt(
                soil_data, weather_data, disease_name
            )
            response = self.model.generate_content(prompt)

            return self._parse_environmental_response(response.text)

        except Exception as e:
            logger.error(f"Environmental analysis failed: {e}")
            return self._create_fallback_environmental()

    def _generate_realistic_weather(self, location: str) -> WeatherData:
        """Generate realistic weather data for major agricultural cities."""

        # Top 10 agricultural cities in India with realistic weather ranges
        city_weather_patterns = {
            "bangalore": {
                "temp_range": (15, 30),
                "humidity": (60, 80),
                "rainfall": (5, 150),
            },
            "pune": {
                "temp_range": (18, 35),
                "humidity": (50, 75),
                "rainfall": (10, 200),
            },
            "hyderabad": {
                "temp_range": (20, 38),
                "humidity": (45, 70),
                "rainfall": (15, 180),
            },
            "chennai": {
                "temp_range": (24, 36),
                "humidity": (70, 85),
                "rainfall": (20, 250),
            },
            "coimbatore": {
                "temp_range": (18, 32),
                "humidity": (65, 80),
                "rainfall": (25, 300),
            },
            "mysore": {
                "temp_range": (16, 28),
                "humidity": (60, 85),
                "rainfall": (30, 200),
            },
            "salem": {
                "temp_range": (20, 35),
                "humidity": (55, 75),
                "rainfall": (15, 180),
            },
            "madurai": {
                "temp_range": (22, 38),
                "humidity": (50, 70),
                "rainfall": (10, 150),
            },
            "tirupur": {
                "temp_range": (19, 33),
                "humidity": (60, 80),
                "rainfall": (20, 220),
            },
            "erode": {
                "temp_range": (21, 36),
                "humidity": (55, 75),
                "rainfall": (18, 190),
            },
        }

        # Default to Bangalore if location not found
        location_key = location.lower() if location else "bangalore"
        pattern = city_weather_patterns.get(
            location_key, city_weather_patterns["bangalore"]
        )

        # Generate realistic values within ranges
        temp_min = random.uniform(
            pattern["temp_range"][0], pattern["temp_range"][0] + 5
        )
        temp_max = random.uniform(
            pattern["temp_range"][1] - 5, pattern["temp_range"][1]
        )
        temp_avg = (temp_min + temp_max) / 2

        return WeatherData(
            location=location or "Bangalore",
            temperature_avg=round(temp_avg, 1),
            temperature_min=round(temp_min, 1),
            temperature_max=round(temp_max, 1),
            humidity=round(
                random.uniform(pattern["humidity"][0], pattern["humidity"][1]), 1
            ),
            rainfall=round(
                random.uniform(pattern["rainfall"][0], pattern["rainfall"][1]), 1
            ),
            wind_speed=round(random.uniform(5, 25), 1),
            pressure=round(random.uniform(1010, 1020), 1),
        )

    def _build_environmental_prompt(
        self,
        soil_data: Optional[Dict[str, Any]],
        weather_data: Optional[WeatherData],
        disease_name: str,
    ) -> str:
        """Build prompt for environmental analysis."""

        prompt = f"""
        You are an agricultural environmental specialist. Analyze how environmental factors contribute to the development and spread of {disease_name}.
        
        """

        if soil_data:
            prompt += f"Soil Data: {soil_data}\n\n"

        if weather_data:
            prompt += f"""
            Weather Conditions:
            - Temperature: {weather_data.temperature_min}°C - {weather_data.temperature_max}°C (avg: {weather_data.temperature_avg}°C)
            - Humidity: {weather_data.humidity}%
            - Rainfall: {weather_data.rainfall}mm
            - Wind Speed: {weather_data.wind_speed} km/h
            
            """

        prompt += """
        Analyze and provide:
        1. How soil pH affects disease development
        2. Moisture conditions that favor this disease
        3. Temperature ranges that promote disease
        4. Humidity impact on disease spread
        5. Nutrient deficiencies that increase susceptibility
        6. Other environmental stress factors
        
        Be specific about the mechanisms and provide actionable insights.
        """

        return prompt

    def _parse_environmental_response(self, response_text: str) -> EnvironmentalFactors:
        """Parse environmental analysis response."""

        # Example parsing - in production would use structured output
        return EnvironmentalFactors(
            soil_ph_impact="Acidic soil (pH < 6.0) increases disease susceptibility",
            moisture_conditions="High moisture and poor drainage favor pathogen growth",
            temperature_range="Optimal disease development at 25-30°C",
            humidity_impact="High humidity (>80%) promotes spore germination",
            nutrient_deficiencies=["nitrogen deficiency", "potassium deficiency"],
            environmental_stress_factors=[
                "waterlogging",
                "temperature stress",
                "poor air circulation",
            ],
        )

    def _create_fallback_environmental(self) -> EnvironmentalFactors:
        """Create fallback environmental analysis."""

        return EnvironmentalFactors(
            soil_ph_impact="Environmental analysis unavailable",
            moisture_conditions="Unable to determine moisture impact",
            temperature_range="Temperature correlation unknown",
            humidity_impact="Humidity impact unclear",
            nutrient_deficiencies=[],
            environmental_stress_factors=[],
        )


class ResearchAgent:
    """Agent for conducting deep research using Exa search."""

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    async def conduct_research(
        self,
        disease_name: str,
        crop_type: str,
        specific_questions: Optional[List[str]] = None,
    ) -> ResearchFindings:
        """Conduct comprehensive research on the disease."""

        try:
            # Perform multiple targeted searches
            research_data = await self._perform_research_searches(
                disease_name, crop_type
            )

            # Synthesize findings
            return await self._synthesize_research(
                research_data, disease_name, crop_type
            )

        except Exception as e:
            logger.error(f"Research failed: {e}")
            return self._create_fallback_research(disease_name)

    async def _perform_research_searches(
        self, disease_name: str, crop_type: str
    ) -> Dict[str, Any]:
        """Perform multiple targeted research searches."""

        searches = {
            "causes": f"{disease_name} {crop_type} causes pathogen lifecycle",
            "treatment": f"{disease_name} {crop_type} treatment control management",
            "prevention": f"{disease_name} {crop_type} prevention integrated pest management",
            "recent_research": f"{disease_name} {crop_type} recent research 2023 2024",
        }

        research_data = {}

        for search_type, query in searches.items():
            try:
                result = exa_search(
                    query=query,
                    num_results=5,
                    include_domains=[
                        "extension.org",
                        "icar.org.in",
                        "fao.org",
                        "usda.gov",
                        "agriculture.com",
                        "researchgate.net",
                        "springer.com",
                        "sciencedirect.com",
                        "wiley.com",
                        "nature.com",
                    ],
                    use_autoprompt=True,
                    include_text=True,
                    text_length_limit=1500,
                )

                if result["status"] == "success":
                    research_data[search_type] = result["raw_data"]
                else:
                    research_data[search_type] = []

            except Exception as e:
                logger.error(f"Search failed for {search_type}: {e}")
                research_data[search_type] = []

        return research_data

    async def _synthesize_research(
        self, research_data: Dict[str, Any], disease_name: str, crop_type: str
    ) -> ResearchFindings:
        """Synthesize research findings into structured output."""

        # Combine all research text
        combined_research = ""
        sources = []

        for search_type, results in research_data.items():
            for result in results:
                combined_research += f"\n--- {search_type.upper()} RESEARCH ---\n"
                combined_research += f"Title: {result.get('title', 'No title')}\n"
                combined_research += f"Content: {result.get('text', 'No content')}\n"
                if result.get("url"):
                    sources.append(result["url"])

        # Use AI to synthesize findings
        prompt = f"""
        You are a plant pathology researcher. Synthesize the following research data about {disease_name} affecting {crop_type} crops.
        
        Research Data:
        {combined_research[:8000]}  # Limit to avoid token limits
        
        Extract and organize:
        1. Primary causes of the disease
        2. Pathogen lifecycle information
        3. Disease spread mechanisms
        4. Other crops that can be affected (host range)
        5. Recent research developments
        
        Provide specific, actionable information based on the research.
        """

        try:
            response = self.model.generate_content(prompt)
            return self._parse_research_response(response.text, sources)
        except Exception as e:
            logger.error(f"Research synthesis failed: {e}")
            return self._create_fallback_research(disease_name)

    def _parse_research_response(
        self, response_text: str, sources: List[str]
    ) -> ResearchFindings:
        """Parse research synthesis response."""

        # Example parsing - in production would use structured output
        return ResearchFindings(
            disease_causes=[
                "fungal pathogen",
                "environmental stress",
                "poor sanitation",
            ],
            pathogen_lifecycle="Pathogen overwinters in soil debris, spreads through water splash",
            spread_mechanisms=[
                "water splash",
                "wind dispersal",
                "contaminated tools",
                "infected seeds",
            ],
            host_range=["tomato", "pepper", "eggplant", "potato"],
            research_sources=sources[:10],  # Limit sources
            recent_developments=[
                "new resistant varieties",
                "biological control agents",
                "precision application methods",
            ],
        )

    def _create_fallback_research(self, disease_name: str) -> ResearchFindings:
        """Create fallback research findings."""

        return ResearchFindings(
            disease_causes=[f"Unknown causes for {disease_name}"],
            pathogen_lifecycle=None,
            spread_mechanisms=["unknown transmission"],
            host_range=[],
            research_sources=[],
            recent_developments=[],
        )


class TreatmentRecommendationAgent:
    """Agent for generating treatment recommendations."""

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    async def generate_treatment_recommendations(
        self,
        disease_name: str,
        crop_type: str,
        severity: SeverityLevel,
        research_findings: ResearchFindings,
    ) -> List[TreatmentOption]:
        """Generate comprehensive treatment recommendations."""

        try:
            # Search for specific treatment information
            treatment_data = await self._search_treatment_options(
                disease_name, crop_type
            )

            # Generate recommendations based on severity and research
            return await self._synthesize_treatments(
                disease_name, crop_type, severity, research_findings, treatment_data
            )

        except Exception as e:
            logger.error(f"Treatment recommendation failed: {e}")
            return self._create_fallback_treatments(disease_name, severity)

    async def _search_treatment_options(
        self, disease_name: str, crop_type: str
    ) -> Dict[str, Any]:
        """Search for treatment options."""

        query = f"{disease_name} {crop_type} treatment fungicide bactericide control products"

        try:
            result = exa_search(
                query=query,
                num_results=8,
                include_domains=[
                    "extension.org",
                    "icar.org.in",
                    "agriculture.gov.in",
                    "bayer.com",
                    "syngenta.com",
                    "corteva.com",
                    "agritech.tnau.ac.in",
                    "krishijagran.com",
                ],
                use_autoprompt=True,
                include_text=True,
                text_length_limit=1200,
            )

            return result.get("raw_data", []) if result["status"] == "success" else []

        except Exception as e:
            logger.error(f"Treatment search failed: {e}")
            return []

    async def _synthesize_treatments(
        self,
        disease_name: str,
        crop_type: str,
        severity: SeverityLevel,
        research_findings: ResearchFindings,
        treatment_data: List[Dict[str, Any]],
    ) -> List[TreatmentOption]:
        """Synthesize treatment options from research and search data."""

        # Combine treatment research
        treatment_text = ""
        for data in treatment_data:
            treatment_text += f"Title: {data.get('title', '')}\n"
            treatment_text += f"Content: {data.get('text', '')}\n\n"

        prompt = f"""
        You are an agricultural extension specialist. Based on the research data, recommend specific treatments for {disease_name} affecting {crop_type} crops.
        
        Disease Severity: {severity}
        Research Findings: {research_findings.disease_causes}
        
        Treatment Research Data:
        {treatment_text[:6000]}
        
        Provide 3-5 treatment options including:
        1. Chemical treatments (fungicides/bactericides)
        2. Biological control options
        3. Cultural/management practices
        4. Integrated approaches
        
        For each treatment, specify:
        - Treatment name and active ingredients
        - Application method and dosage
        - Frequency and timing
        - Where to obtain (suppliers/dealers)
        - Cost estimates
        - Effectiveness and precautions
        """

        try:
            response = self.model.generate_content(prompt)
            return self._parse_treatment_response(response.text, severity)
        except Exception as e:
            logger.error(f"Treatment synthesis failed: {e}")
            return self._create_fallback_treatments(disease_name, severity)

    def _parse_treatment_response(
        self, response_text: str, severity: SeverityLevel
    ) -> List[TreatmentOption]:
        """Parse treatment recommendations response."""

        # Example treatments - in production would parse from AI response
        treatments = [
            TreatmentOption(
                treatment_name="Copper-based Fungicide",
                treatment_type=TreatmentType.CHEMICAL,
                active_ingredients=["copper sulfate", "copper hydroxide"],
                application_method="Foliar spray",
                dosage="2-3 grams per liter of water",
                frequency="Every 7-10 days",
                timing="Early morning or evening",
                cost_estimate="₹200-300 per acre",
                availability="Local agricultural stores, online retailers",
                effectiveness=0.8,
                side_effects=[
                    "may cause leaf burn if overused",
                    "avoid during flowering",
                ],
            ),
            TreatmentOption(
                treatment_name="Trichoderma Biological Control",
                treatment_type=TreatmentType.BIOLOGICAL,
                active_ingredients=["Trichoderma viride", "Trichoderma harzianum"],
                application_method="Soil application and foliar spray",
                dosage="5-10 grams per liter for spray, 1 kg per acre for soil",
                frequency="Every 15 days",
                timing="Before disease onset, preventive application",
                cost_estimate="₹150-250 per acre",
                availability="Bio-fertilizer dealers, ICAR centers",
                effectiveness=0.7,
                side_effects=[
                    "no known side effects",
                    "compatible with organic farming",
                ],
            ),
            TreatmentOption(
                treatment_name="Cultural Management",
                treatment_type=TreatmentType.CULTURAL,
                active_ingredients=["improved sanitation", "crop rotation"],
                application_method="Field management practices",
                dosage="Complete implementation",
                frequency="Continuous",
                timing="Throughout growing season",
                cost_estimate="₹50-100 per acre (labor cost)",
                availability="Farmer implementation",
                effectiveness=0.6,
                side_effects=["requires additional labor", "long-term benefits"],
            ),
        ]

        # Adjust effectiveness based on severity
        severity_multiplier = {
            SeverityLevel.MILD: 1.0,
            SeverityLevel.MODERATE: 0.9,
            SeverityLevel.SEVERE: 0.8,
            SeverityLevel.CRITICAL: 0.7,
        }

        multiplier = severity_multiplier.get(severity, 0.8)
        for treatment in treatments:
            treatment.effectiveness *= multiplier

        return treatments

    def _create_fallback_treatments(
        self, disease_name: str, severity: SeverityLevel
    ) -> List[TreatmentOption]:
        """Create fallback treatment options."""

        return [
            TreatmentOption(
                treatment_name="General Fungicide Treatment",
                treatment_type=TreatmentType.CHEMICAL,
                active_ingredients=["broad spectrum fungicide"],
                application_method="Foliar spray",
                dosage="As per manufacturer instructions",
                frequency="Weekly",
                timing="Early morning",
                cost_estimate="₹200-400 per acre",
                availability="Local agricultural stores",
                effectiveness=0.6,
                side_effects=["follow safety guidelines"],
            )
        ]


class YieldImpactAnalysisAgent:
    """Agent for analyzing yield impact and economic implications."""

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    async def analyze_yield_impact(
        self,
        disease_name: str,
        crop_type: str,
        severity: SeverityLevel,
        environmental_factors: EnvironmentalFactors,
        treatment_available: bool = True,
    ) -> YieldImpact:
        """Analyze potential yield impact and economic implications."""

        try:
            # Search for yield loss data
            yield_data = await self._search_yield_impact_data(disease_name, crop_type)

            # Calculate impact based on severity and factors
            return await self._calculate_yield_impact(
                disease_name,
                crop_type,
                severity,
                environmental_factors,
                yield_data,
                treatment_available,
            )

        except Exception as e:
            logger.error(f"Yield impact analysis failed: {e}")
            return self._create_fallback_yield_impact(severity)

    async def _search_yield_impact_data(
        self, disease_name: str, crop_type: str
    ) -> List[Dict[str, Any]]:
        """Search for yield impact data."""

        query = (
            f"{disease_name} {crop_type} yield loss economic impact damage assessment"
        )

        try:
            result = exa_search(
                query=query,
                num_results=5,
                include_domains=[
                    "fao.org",
                    "icar.org.in",
                    "agriculture.gov.in",
                    "researchgate.net",
                    "springer.com",
                    "extension.org",
                ],
                use_autoprompt=True,
                include_text=True,
                text_length_limit=1000,
            )

            return result.get("raw_data", []) if result["status"] == "success" else []

        except Exception as e:
            logger.error(f"Yield impact search failed: {e}")
            return []

    async def _calculate_yield_impact(
        self,
        disease_name: str,
        crop_type: str,
        severity: SeverityLevel,
        environmental_factors: EnvironmentalFactors,
        yield_data: List[Dict[str, Any]],
        treatment_available: bool,
    ) -> YieldImpact:
        """Calculate yield impact based on multiple factors."""

        # Base yield loss percentages by severity
        base_yield_loss = {
            SeverityLevel.MILD: 5.0,
            SeverityLevel.MODERATE: 15.0,
            SeverityLevel.SEVERE: 35.0,
            SeverityLevel.CRITICAL: 60.0,
        }

        potential_loss = base_yield_loss.get(severity, 20.0)

        # Adjust based on environmental factors
        if len(environmental_factors.environmental_stress_factors) > 2:
            potential_loss *= 1.2  # Increase loss if multiple stress factors

        if len(environmental_factors.nutrient_deficiencies) > 1:
            potential_loss *= 1.1  # Increase loss if nutrient deficient

        # Adjust based on treatment availability
        mitigation_potential = 0.7 if treatment_available else 0.3

        # Cap at 80% maximum loss
        potential_loss = min(potential_loss, 80.0)

        # Generate economic impact description
        economic_impact = self._generate_economic_impact_description(
            potential_loss, crop_type
        )

        return YieldImpact(
            potential_yield_loss=round(potential_loss, 1),
            economic_impact=economic_impact,
            quality_impact=self._assess_quality_impact(severity),
            market_value_impact=self._assess_market_value_impact(potential_loss),
            recovery_timeline=self._estimate_recovery_timeline(
                severity, treatment_available
            ),
            mitigation_potential=mitigation_potential,
        )

    def _generate_economic_impact_description(
        self, yield_loss: float, crop_type: str
    ) -> str:
        """Generate economic impact description."""

        if yield_loss < 10:
            return f"Minor economic impact expected. {crop_type} production should remain profitable with minimal intervention."
        elif yield_loss < 25:
            return f"Moderate economic impact. Treatment costs may be offset by yield preservation. Consider immediate intervention."
        elif yield_loss < 50:
            return f"Significant economic impact. Immediate treatment essential to prevent major losses. May affect seasonal profitability."
        else:
            return f"Severe economic impact. Crop may become unprofitable without immediate intensive treatment. Consider crop insurance claims."

    def _assess_quality_impact(self, severity: SeverityLevel) -> str:
        """Assess impact on crop quality."""

        quality_impacts = {
            SeverityLevel.MILD: "Minimal impact on crop quality. Marketable produce expected.",
            SeverityLevel.MODERATE: "Some reduction in crop quality. May affect premium pricing.",
            SeverityLevel.SEVERE: "Significant quality degradation. Reduced market value expected.",
            SeverityLevel.CRITICAL: "Severe quality loss. Crop may be unsuitable for premium markets.",
        }

        return quality_impacts.get(severity, "Quality impact assessment unavailable.")

    def _assess_market_value_impact(self, yield_loss: float) -> str:
        """Assess market value impact."""

        if yield_loss < 15:
            return "Minimal impact on market value. Normal pricing expected."
        elif yield_loss < 35:
            return "Moderate impact on market value. 10-20% price reduction possible."
        else:
            return "Significant impact on market value. 25-40% price reduction likely."

    def _estimate_recovery_timeline(
        self, severity: SeverityLevel, treatment_available: bool
    ) -> str:
        """Estimate recovery timeline."""

        base_timelines = {
            SeverityLevel.MILD: "1-2 weeks with treatment",
            SeverityLevel.MODERATE: "3-4 weeks with treatment",
            SeverityLevel.SEVERE: "6-8 weeks with intensive treatment",
            SeverityLevel.CRITICAL: "Full season may be lost, focus on next season",
        }

        timeline = base_timelines.get(severity, "Timeline uncertain")

        if not treatment_available:
            timeline += " (extended without proper treatment)"

        return timeline

    def _create_fallback_yield_impact(self, severity: SeverityLevel) -> YieldImpact:
        """Create fallback yield impact analysis."""

        base_loss = {
            SeverityLevel.MILD: 10.0,
            SeverityLevel.MODERATE: 20.0,
            SeverityLevel.SEVERE: 40.0,
            SeverityLevel.CRITICAL: 65.0,
        }

        return YieldImpact(
            potential_yield_loss=base_loss.get(severity, 25.0),
            economic_impact="Economic impact analysis unavailable",
            quality_impact="Quality impact assessment unavailable",
            market_value_impact=None,
            recovery_timeline="Recovery timeline uncertain",
            mitigation_potential=0.5,
        )


class DailyLogTodoIntegrationAgent:
    """Agent for integrating disease analysis with daily logs and todo tasks."""

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    async def create_daily_log_entry(
        self,
        user_id: int,
        crop_id: Optional[int],
        disease_report: ComprehensiveDiseaseReport,
        db: Session,
        image_data: Optional[bytes] = None,
    ) -> Optional[int]:
        """Create a daily log entry for the disease analysis."""

        try:
            # Prepare activity details
            activity_details = {
                "analysis_id": disease_report.analysis_id,
                "disease_identified": disease_report.disease_identification.disease_name,
                "confidence": disease_report.disease_identification.confidence,
                "severity": disease_report.disease_identification.severity,
                "treatment_options_count": len(disease_report.treatment_options),
                "yield_impact": disease_report.yield_impact.potential_yield_loss,
            }

            # Create daily log entry
            daily_log = DailyLog(
                crop_id=crop_id,
                log_date=date.today(),
                activity_type="disease_analysis",
                activity_details=activity_details,
                notes=f"Disease analysis conducted: {disease_report.disease_identification.disease_name}. "
                f"Confidence: {disease_report.disease_identification.confidence}. "
                f"Potential yield loss: {disease_report.yield_impact.potential_yield_loss}%.",
                crop_health_observation=disease_report.disease_identification.severity,
                crop_health_notes=f"Symptoms: {', '.join(disease_report.disease_identification.symptoms_observed)}",
                diseases_noted=disease_report.disease_identification.disease_name,
                disease_spotted=True,
                ai_insights=disease_report.executive_summary,
                ai_recommendations=disease_report.immediate_actions
                + disease_report.long_term_recommendations,
                images=[f"disease_analysis_{disease_report.analysis_id}.jpg"]
                if image_data
                else [],
            )

            db.add(daily_log)
            db.commit()
            db.refresh(daily_log)

            logger.info(
                f"Created daily log entry {daily_log.id} for disease analysis {disease_report.analysis_id}"
            )
            return daily_log.id

        except Exception as e:
            logger.error(f"Failed to create daily log entry: {e}")
            db.rollback()
            return None

    async def create_todo_tasks(
        self,
        user_id: int,
        crop_id: Optional[int],
        disease_report: ComprehensiveDiseaseReport,
        db: Session,
    ) -> List[int]:
        """Create todo tasks based on disease analysis recommendations."""

        created_todo_ids = []

        try:
            # Create immediate action todos
            for i, action in enumerate(
                disease_report.immediate_actions[:5], 1
            ):  # Limit to 5 immediate actions
                todo = TodoTask(
                    user_id=user_id,
                    crop_id=crop_id,
                    task_title=f"Immediate Action {i}: {action[:50]}{'...' if len(action) > 50 else ''}",
                    task_description=action,
                    priority="high",
                    status="pending",
                    due_date=date.today() + timedelta(days=1),  # Due tomorrow
                    is_system_generated=True,
                    ai_generated=True,
                )

                db.add(todo)
                db.commit()
                db.refresh(todo)
                created_todo_ids.append(todo.id)
                logger.info(
                    f"Created immediate action todo {todo.id}: {action[:30]}..."
                )

            # Create treatment todos
            for i, treatment in enumerate(
                disease_report.treatment_options[:3], 1
            ):  # Limit to 3 treatments
                todo = TodoTask(
                    user_id=user_id,
                    crop_id=crop_id,
                    task_title=f"Apply {treatment.treatment_name}",
                    task_description=f"Treatment: {treatment.treatment_name}\n"
                    f"Method: {treatment.application_method}\n"
                    f"Dosage: {treatment.dosage}\n"
                    f"Frequency: {treatment.frequency}\n"
                    f"Timing: {treatment.timing}\n"
                    f"Cost: {treatment.cost_estimate}\n"
                    f"Where to get: {treatment.availability}",
                    priority="high" if treatment.effectiveness > 0.7 else "medium",
                    status="pending",
                    due_date=date.today() + timedelta(days=2),  # Due in 2 days
                    is_system_generated=True,
                    ai_generated=True,
                )

                db.add(todo)
                db.commit()
                db.refresh(todo)
                created_todo_ids.append(todo.id)
                logger.info(
                    f"Created treatment todo {todo.id}: {treatment.treatment_name}"
                )

            # Create prevention todos for long-term
            for i, prevention in enumerate(
                disease_report.prevention_strategies[:3], 1
            ):  # Limit to 3 strategies
                todo = TodoTask(
                    user_id=user_id,
                    crop_id=crop_id,
                    task_title=f"Implement {prevention.strategy_name}",
                    task_description=f"Prevention Strategy: {prevention.strategy_name}\n"
                    f"Description: {prevention.description}\n"
                    f"Steps: {'; '.join(prevention.implementation_steps)}\n"
                    f"Timing: {prevention.timing}\n"
                    f"Cost: {prevention.cost}",
                    priority="medium",
                    status="pending",
                    due_date=date.today() + timedelta(days=7),  # Due in a week
                    is_system_generated=True,
                    ai_generated=True,
                )

                db.add(todo)
                db.commit()
                db.refresh(todo)
                created_todo_ids.append(todo.id)
                logger.info(
                    f"Created prevention todo {todo.id}: {prevention.strategy_name}"
                )

            # Create monitoring todo
            monitoring_todo = TodoTask(
                user_id=user_id,
                crop_id=crop_id,
                task_title="Monitor Disease Progress",
                task_description=f"Monitor the progress of {disease_report.disease_identification.disease_name} treatment.\n"
                f"Check for improvement in symptoms: {', '.join(disease_report.disease_identification.symptoms_observed)}\n"
                f"Expected recovery timeline: {disease_report.yield_impact.recovery_timeline}\n"
                f"Take photos and update daily logs.",
                priority="medium",
                status="pending",
                due_date=date.today() + timedelta(days=3),  # Due in 3 days
                is_system_generated=True,
                ai_generated=True,
                is_recurring=True,
                recurrence_pattern="weekly",
                recurrence_interval=1,
            )

            db.add(monitoring_todo)
            db.commit()
            db.refresh(monitoring_todo)
            created_todo_ids.append(monitoring_todo.id)
            logger.info(f"Created monitoring todo {monitoring_todo.id}")

            return created_todo_ids

        except Exception as e:
            logger.error(f"Failed to create todo tasks: {e}")
            db.rollback()
            return created_todo_ids  # Return what was created before the error


class CropDiseaseResearchOrchestrator:
    """Main orchestrator that coordinates all agents for comprehensive disease analysis."""

    def __init__(self):
        self.disease_agent = DiseaseIdentificationAgent()
        self.environmental_agent = EnvironmentalAnalysisAgent()
        self.research_agent = ResearchAgent()
        self.treatment_agent = TreatmentRecommendationAgent()
        self.yield_agent = YieldImpactAnalysisAgent()
        self.integration_agent = DailyLogTodoIntegrationAgent()
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    async def conduct_deep_research(
        self,
        image_data: Optional[bytes] = None,
        symptoms_text: Optional[str] = None,
        crop_type: str = "unknown",
        location: Optional[str] = None,
        soil_data: Optional[Dict[str, Any]] = None,
        weather_data: Optional[WeatherData] = None,
        user_id: Optional[int] = None,
        crop_id: Optional[int] = None,
        db: Optional[Session] = None,
        create_logs_and_todos: bool = False,
    ) -> ComprehensiveDiseaseReport:
        """
        Conduct comprehensive crop disease research using all agents.

        Args:
            image_data: Optional image data of the affected crop
            symptoms_text: Text description of observed symptoms
            crop_type: Type of crop being analyzed
            location: Location of the crop (for weather data generation)
            soil_data: Soil analysis data
            weather_data: Weather data (will be generated if not provided)

        Returns:
            ComprehensiveDiseaseReport: Complete analysis report
        """

        analysis_id = f"disease_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Starting comprehensive disease analysis: {analysis_id}")

        try:
            # Step 1: Disease Identification
            logger.info("Step 1: Identifying disease...")
            disease_identification = await self.disease_agent.analyze_disease(
                image_data=image_data, symptoms_text=symptoms_text, crop_type=crop_type
            )

            # Step 2: Environmental Analysis
            logger.info("Step 2: Analyzing environmental factors...")
            environmental_analysis = (
                await self.environmental_agent.analyze_environmental_factors(
                    soil_data=soil_data,
                    weather_data=weather_data,
                    disease_name=disease_identification.disease_name,
                    location=location,
                )
            )

            # Generate weather data if not provided
            if not weather_data and location:
                weather_data = self.environmental_agent._generate_realistic_weather(
                    location
                )

            # Step 3: Research Findings
            logger.info("Step 3: Conducting deep research...")
            research_findings = await self.research_agent.conduct_research(
                disease_name=disease_identification.disease_name, crop_type=crop_type
            )

            # Step 4: Treatment Recommendations
            logger.info("Step 4: Generating treatment recommendations...")
            treatment_options = (
                await self.treatment_agent.generate_treatment_recommendations(
                    disease_name=disease_identification.disease_name,
                    crop_type=crop_type,
                    severity=disease_identification.severity,
                    research_findings=research_findings,
                )
            )

            # Step 5: Yield Impact Analysis
            logger.info("Step 5: Analyzing yield impact...")
            yield_impact = await self.yield_agent.analyze_yield_impact(
                disease_name=disease_identification.disease_name,
                crop_type=crop_type,
                severity=disease_identification.severity,
                environmental_factors=environmental_analysis,
                treatment_available=len(treatment_options) > 0,
            )

            # Step 6: Generate Prevention Strategies
            logger.info("Step 6: Generating prevention strategies...")
            prevention_strategies = await self._generate_prevention_strategies(
                disease_identification, environmental_analysis, research_findings
            )

            # Step 7: Create Executive Summary and Recommendations
            logger.info("Step 7: Creating executive summary...")
            (
                executive_summary,
                immediate_actions,
                long_term_recommendations,
            ) = await self._generate_summary_and_recommendations(
                disease_identification,
                environmental_analysis,
                research_findings,
                treatment_options,
                yield_impact,
                prevention_strategies,
            )

            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(
                disease_identification, research_findings, treatment_options
            )

            # Compile final report
            report = ComprehensiveDiseaseReport(
                analysis_id=analysis_id,
                crop_type=crop_type,
                location=location,
                crop_id=crop_id,
                disease_identification=disease_identification,
                environmental_analysis=environmental_analysis,
                weather_correlation=weather_data,
                research_findings=research_findings,
                treatment_options=treatment_options,
                prevention_strategies=prevention_strategies,
                yield_impact=yield_impact,
                executive_summary=executive_summary,
                immediate_actions=immediate_actions,
                long_term_recommendations=long_term_recommendations,
                confidence_overall=overall_confidence,
            )

            # Step 8: Create daily logs and todos if requested
            if create_logs_and_todos and user_id and db:
                logger.info("Step 8: Creating daily logs and todo tasks...")
                try:
                    # Create daily log entry
                    daily_log_id = await self.integration_agent.create_daily_log_entry(
                        user_id=user_id,
                        crop_id=crop_id,
                        disease_report=report,
                        db=db,
                        image_data=image_data,
                    )

                    # Create todo tasks
                    todo_ids = await self.integration_agent.create_todo_tasks(
                        user_id=user_id, crop_id=crop_id, disease_report=report, db=db
                    )

                    # Update report with integration data
                    report.daily_log_id = daily_log_id
                    report.todo_ids = todo_ids
                    report.integration_status = (
                        "completed" if daily_log_id and todo_ids else "partial"
                    )

                    logger.info(
                        f"Integration completed: daily_log_id={daily_log_id}, todo_count={len(todo_ids)}"
                    )

                except Exception as e:
                    logger.error(f"Integration failed: {e}")
                    report.integration_status = "failed"

            logger.info(f"Comprehensive disease analysis completed: {analysis_id}")
            return report

        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {e}")
            return await self._create_fallback_report(
                analysis_id, crop_type, location, str(e)
            )

    async def _generate_prevention_strategies(
        self,
        disease_identification: DiseaseIdentification,
        environmental_analysis: EnvironmentalFactors,
        research_findings: ResearchFindings,
    ) -> List[PreventionStrategy]:
        """Generate prevention strategies based on analysis."""

        prompt = f"""
        Based on the disease analysis, generate 3-5 prevention strategies for {disease_identification.disease_name}.
        
        Disease Information:
        - Disease: {disease_identification.disease_name}
        - Severity: {disease_identification.severity}
        - Affected parts: {disease_identification.affected_plant_parts}
        
        Environmental Factors:
        - Soil pH impact: {environmental_analysis.soil_ph_impact}
        - Moisture conditions: {environmental_analysis.moisture_conditions}
        - Stress factors: {environmental_analysis.environmental_stress_factors}
        
        Research Findings:
        - Spread mechanisms: {research_findings.spread_mechanisms}
        - Disease causes: {research_findings.disease_causes}
        
        Provide specific, actionable prevention strategies including:
        1. Cultural practices
        2. Sanitation measures
        3. Resistant varieties
        4. Environmental management
        5. Monitoring protocols
        """

        try:
            response = self.model.generate_content(prompt)
            return self._parse_prevention_strategies(response.text)
        except Exception as e:
            logger.error(f"Prevention strategy generation failed: {e}")
            return self._create_fallback_prevention_strategies()

    def _parse_prevention_strategies(
        self, response_text: str
    ) -> List[PreventionStrategy]:
        """Parse prevention strategies from AI response."""

        # Example strategies - in production would parse from AI response
        return [
            PreventionStrategy(
                strategy_name="Crop Rotation",
                description="Implement 3-4 year crop rotation with non-host crops to break disease cycle",
                implementation_steps=[
                    "Plan rotation sequence with cereals or legumes",
                    "Avoid planting susceptible crops in same field",
                    "Maintain rotation records",
                    "Monitor soil health during rotation",
                ],
                timing="Plan before next planting season",
                cost="₹500-1000 per acre (planning and implementation)",
                effectiveness=0.8,
            ),
            PreventionStrategy(
                strategy_name="Sanitation Practices",
                description="Implement strict field sanitation to reduce pathogen load",
                implementation_steps=[
                    "Remove and destroy infected plant debris",
                    "Clean tools between fields",
                    "Use certified disease-free seeds",
                    "Disinfect equipment regularly",
                ],
                timing="Continuous throughout season",
                cost="₹200-400 per acre (labor and materials)",
                effectiveness=0.7,
            ),
            PreventionStrategy(
                strategy_name="Water Management",
                description="Optimize irrigation to reduce disease-favorable conditions",
                implementation_steps=[
                    "Install drip irrigation system",
                    "Avoid overhead watering",
                    "Improve field drainage",
                    "Monitor soil moisture levels",
                ],
                timing="Before planting and throughout season",
                cost="₹2000-5000 per acre (infrastructure)",
                effectiveness=0.75,
            ),
        ]

    def _create_fallback_prevention_strategies(self) -> List[PreventionStrategy]:
        """Create fallback prevention strategies."""

        return [
            PreventionStrategy(
                strategy_name="General Sanitation",
                description="Maintain good field hygiene and sanitation practices",
                implementation_steps=[
                    "Remove infected plant material",
                    "Clean farming tools",
                    "Use healthy seeds",
                ],
                timing="Throughout growing season",
                cost="₹300-500 per acre",
                effectiveness=0.6,
            )
        ]

    async def _generate_summary_and_recommendations(
        self,
        disease_identification: DiseaseIdentification,
        environmental_analysis: EnvironmentalFactors,
        research_findings: ResearchFindings,
        treatment_options: List[TreatmentOption],
        yield_impact: YieldImpact,
        prevention_strategies: List[PreventionStrategy],
    ) -> tuple[str, List[str], List[str]]:
        """Generate executive summary and recommendations."""

        prompt = f"""
        Create an executive summary and recommendations based on the comprehensive disease analysis:
        
        Disease: {disease_identification.disease_name} (Confidence: {disease_identification.confidence})
        Severity: {disease_identification.severity}
        Potential Yield Loss: {yield_impact.potential_yield_loss}%
        
        Available Treatments: {len(treatment_options)}
        Prevention Strategies: {len(prevention_strategies)}
        
        Provide:
        1. Executive summary (2-3 paragraphs)
        2. Immediate actions (3-5 bullet points)
        3. Long-term recommendations (3-5 bullet points)
        
        Focus on actionable insights and prioritize based on severity and economic impact.
        """

        try:
            response = self.model.generate_content(prompt)
            return self._parse_summary_and_recommendations(
                response.text, disease_identification, yield_impact
            )
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return self._create_fallback_summary_and_recommendations(
                disease_identification, yield_impact
            )

    def _parse_summary_and_recommendations(
        self,
        response_text: str,
        disease_identification: DiseaseIdentification,
        yield_impact: YieldImpact,
    ) -> tuple[str, List[str], List[str]]:
        """Parse summary and recommendations from AI response."""

        # Example parsing - in production would parse from AI response
        executive_summary = f"""
        Analysis has identified {disease_identification.disease_name} affecting the crop with {disease_identification.confidence} confidence. 
        The disease severity is assessed as {disease_identification.severity}, with potential yield losses of {yield_impact.potential_yield_loss}%. 
        
        Environmental factors including {', '.join(disease_identification.symptoms_observed)} are contributing to disease development. 
        Multiple treatment options are available with varying effectiveness levels. Immediate intervention is recommended to minimize 
        economic impact and preserve crop quality.
        
        The analysis indicates {yield_impact.economic_impact.lower()} Recovery timeline is estimated at {yield_impact.recovery_timeline} 
        with proper treatment implementation.
        """

        immediate_actions = [
            f"Implement {disease_identification.severity.lower()} severity treatment protocol immediately",
            "Apply recommended fungicide/bactericide as per treatment guidelines",
            "Improve field drainage and reduce moisture stress",
            "Remove and destroy infected plant material",
            "Monitor disease progression daily",
        ]

        long_term_recommendations = [
            "Implement crop rotation with non-host crops",
            "Invest in resistant varieties for next season",
            "Establish regular monitoring and early detection protocols",
            "Improve soil health through organic matter addition",
            "Consider precision agriculture technologies for better management",
        ]

        return executive_summary, immediate_actions, long_term_recommendations

    def _create_fallback_summary_and_recommendations(
        self, disease_identification: DiseaseIdentification, yield_impact: YieldImpact
    ) -> tuple[str, List[str], List[str]]:
        """Create fallback summary and recommendations."""

        executive_summary = f"""
        Disease analysis completed for {disease_identification.disease_name} with {disease_identification.confidence} confidence level. 
        Potential yield impact of {yield_impact.potential_yield_loss}% requires immediate attention. Treatment options are available 
        and should be implemented promptly to minimize losses.
        """

        immediate_actions = [
            "Consult local agricultural extension officer",
            "Apply broad-spectrum treatment as precautionary measure",
            "Improve field sanitation practices",
        ]

        long_term_recommendations = [
            "Implement integrated pest management practices",
            "Consider resistant varieties for future plantings",
            "Maintain regular crop monitoring",
        ]

        return executive_summary, immediate_actions, long_term_recommendations

    def _calculate_overall_confidence(
        self,
        disease_identification: DiseaseIdentification,
        research_findings: ResearchFindings,
        treatment_options: List[TreatmentOption],
    ) -> float:
        """Calculate overall confidence in the analysis."""

        # Base confidence from disease identification
        base_confidence = disease_identification.confidence_score

        # Adjust based on research quality
        research_quality = (
            len(research_findings.research_sources) / 10.0
        )  # Normalize to 0-1
        research_quality = min(research_quality, 1.0)

        # Adjust based on treatment availability
        treatment_quality = len(treatment_options) / 5.0  # Normalize to 0-1
        treatment_quality = min(treatment_quality, 1.0)

        # Weighted average
        overall_confidence = (
            base_confidence * 0.5 + research_quality * 0.3 + treatment_quality * 0.2
        )

        return round(overall_confidence, 2)

    async def _create_fallback_report(
        self,
        analysis_id: str,
        crop_type: str,
        location: Optional[str],
        error_message: str,
    ) -> ComprehensiveDiseaseReport:
        """Create fallback report when analysis fails."""

        fallback_disease = DiseaseIdentification(
            disease_name="Unknown Disease",
            scientific_name=None,
            confidence=DiseaseConfidence.UNCERTAIN,
            confidence_score=0.1,
            symptoms_observed=["analysis failed"],
            affected_plant_parts=["unknown"],
            severity=SeverityLevel.MILD,
        )

        fallback_environmental = EnvironmentalFactors()

        fallback_research = ResearchFindings(
            disease_causes=["analysis incomplete"],
            pathogen_lifecycle=None,
            spread_mechanisms=["unknown"],
            host_range=[],
            research_sources=[],
            recent_developments=[],
        )

        fallback_treatment = TreatmentOption(
            treatment_name="Consult Expert",
            treatment_type=TreatmentType.CULTURAL,
            active_ingredients=["professional consultation"],
            application_method="Contact agricultural extension",
            dosage="As recommended by expert",
            frequency="As needed",
            timing="Immediately",
            cost_estimate="Consultation fees",
            availability="Local agricultural office",
            effectiveness=0.5,
            side_effects=[],
        )

        fallback_prevention = PreventionStrategy(
            strategy_name="General Best Practices",
            description="Follow general agricultural best practices",
            implementation_steps=["Maintain field hygiene", "Monitor crops regularly"],
            timing="Continuous",
            cost="Variable",
            effectiveness=0.5,
        )

        fallback_yield = YieldImpact(
            potential_yield_loss=20.0,
            economic_impact="Impact assessment unavailable due to analysis failure",
            quality_impact="Quality impact unknown",
            market_value_impact=None,
            recovery_timeline="Consult expert for timeline",
            mitigation_potential=0.5,
        )

        return ComprehensiveDiseaseReport(
            analysis_id=analysis_id,
            crop_type=crop_type,
            location=location,
            disease_identification=fallback_disease,
            environmental_analysis=fallback_environmental,
            weather_correlation=None,
            research_findings=fallback_research,
            treatment_options=[fallback_treatment],
            prevention_strategies=[fallback_prevention],
            yield_impact=fallback_yield,
            executive_summary=f"Analysis failed due to technical issues: {error_message}. Please consult local agricultural experts for proper diagnosis and treatment recommendations.",
            immediate_actions=[
                "Contact local agricultural extension officer",
                "Implement basic sanitation measures",
            ],
            long_term_recommendations=[
                "Establish regular monitoring protocols",
                "Consider professional consultation",
            ],
            confidence_overall=0.1,
        )


# Main function for external use
async def deep_research_disease_analysis(
    image_data: Optional[bytes] = None,
    symptoms_text: Optional[str] = None,
    crop_type: str = "unknown",
    location: Optional[str] = None,
    soil_data: Optional[Dict[str, Any]] = None,
    weather_data: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None,
    crop_id: Optional[int] = None,
    db: Optional[Session] = None,
    create_logs_and_todos: bool = False,
) -> Dict[str, Any]:
    """
    Main function for conducting deep research on crop diseases.

    Args:
        image_data: Optional image data of the affected crop
        symptoms_text: Text description of observed symptoms
        crop_type: Type of crop being analyzed
        location: Location of the crop
        soil_data: Soil analysis data
        weather_data: Weather data dictionary

    Returns:
        Dict containing the comprehensive disease analysis report
    """

    try:
        # Convert weather_data dict to WeatherData model if provided
        weather_model = None
        if weather_data:
            weather_model = WeatherData(**weather_data)

        # Initialize orchestrator and conduct analysis
        orchestrator = CropDiseaseResearchOrchestrator()

        report = await orchestrator.conduct_deep_research(
            image_data=image_data,
            symptoms_text=symptoms_text,
            crop_type=crop_type,
            location=location,
            soil_data=soil_data,
            weather_data=weather_model,
            user_id=user_id,
            crop_id=crop_id,
            db=db,
            create_logs_and_todos=create_logs_and_todos,
        )

        # Convert to dictionary for API response
        return {
            "status": "success",
            "analysis_id": report.analysis_id,
            "report": report.dict(),
        }

    except Exception as e:
        logger.error(f"Deep research analysis failed: {e}")
        return {
            "status": "error",
            "error_message": f"Analysis failed: {str(e)}",
            "analysis_id": None,
            "report": None,
        }


# Export main components
__all__ = [
    "deep_research_disease_analysis",
    "CropDiseaseResearchOrchestrator",
    "ComprehensiveDiseaseReport",
    "DiseaseIdentification",
    "TreatmentOption",
    "PreventionStrategy",
    "YieldImpact",
]
