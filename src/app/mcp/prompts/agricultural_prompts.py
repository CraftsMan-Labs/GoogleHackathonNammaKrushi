"""
Agricultural Prompts MCP Resource

Provides structured prompts for agricultural assistance and guidance
through the MCP interface.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class AgriculturalPrompts:
    """
    MCP resource for agricultural assistance prompts.

    Provides structured prompts for disease diagnosis, crop planning,
    weather advisory, and other agricultural guidance.
    """

    def __init__(self):
        self.prompt_templates = self._initialize_prompt_templates()

    async def get_disease_diagnosis_prompt(self, args: Dict[str, Any]) -> str:
        """
        Generate a structured disease diagnosis prompt.

        Args:
            args: Arguments containing crop_type, symptoms, location

        Returns:
            Formatted disease diagnosis prompt
        """
        try:
            crop_type = args.get("crop_type", "unknown crop")
            symptoms = args.get("symptoms", "no symptoms provided")
            location = args.get("location", "unspecified location")

            prompt = self.prompt_templates["disease_diagnosis"].format(
                crop_type=crop_type, symptoms=symptoms, location=location
            )

            logger.info(f"Generated disease diagnosis prompt for {crop_type}")
            return prompt

        except Exception as e:
            logger.error(f"Error generating disease diagnosis prompt: {e}")
            return "Error generating disease diagnosis prompt. Please provide crop type and symptoms."

    async def get_crop_planning_prompt(self, args: Dict[str, Any]) -> str:
        """
        Generate a structured crop planning prompt.

        Args:
            args: Arguments containing crop_type, season, soil_type

        Returns:
            Formatted crop planning prompt
        """
        try:
            crop_type = args.get("crop_type", "unknown crop")
            season = args.get("season", "unspecified season")
            soil_type = args.get("soil_type", "unknown soil type")

            prompt = self.prompt_templates["crop_planning"].format(
                crop_type=crop_type, season=season, soil_type=soil_type
            )

            logger.info(f"Generated crop planning prompt for {crop_type}")
            return prompt

        except Exception as e:
            logger.error(f"Error generating crop planning prompt: {e}")
            return "Error generating crop planning prompt. Please provide crop type and season."

    async def get_weather_advisory_prompt(self, args: Dict[str, Any]) -> str:
        """
        Generate a weather advisory prompt.

        Args:
            args: Arguments containing location, current_weather, forecast

        Returns:
            Formatted weather advisory prompt
        """
        try:
            location = args.get("location", "unspecified location")
            current_weather = args.get("current_weather", "unknown conditions")
            forecast = args.get("forecast", "no forecast available")

            prompt = self.prompt_templates["weather_advisory"].format(
                location=location, current_weather=current_weather, forecast=forecast
            )

            logger.info(f"Generated weather advisory prompt for {location}")
            return prompt

        except Exception as e:
            logger.error(f"Error generating weather advisory prompt: {e}")
            return "Error generating weather advisory prompt. Please provide location and weather information."

    async def get_soil_analysis_prompt(self, args: Dict[str, Any]) -> str:
        """
        Generate a soil analysis prompt.

        Args:
            args: Arguments containing soil_data, crop_plans, location

        Returns:
            Formatted soil analysis prompt
        """
        try:
            soil_data = args.get("soil_data", "no soil data provided")
            crop_plans = args.get("crop_plans", "no crop plans specified")
            location = args.get("location", "unspecified location")

            prompt = self.prompt_templates["soil_analysis"].format(
                soil_data=soil_data, crop_plans=crop_plans, location=location
            )

            logger.info(f"Generated soil analysis prompt for {location}")
            return prompt

        except Exception as e:
            logger.error(f"Error generating soil analysis prompt: {e}")
            return "Error generating soil analysis prompt. Please provide soil data and crop plans."

    def _initialize_prompt_templates(self) -> Dict[str, str]:
        """Initialize all prompt templates."""
        return {
            "disease_diagnosis": """
You are an expert agricultural pathologist specializing in crop disease diagnosis and management. Please analyze the following crop health issue and provide comprehensive recommendations.

**Crop Information:**
- Crop Type: {crop_type}
- Location: {location}
- Observed Symptoms: {symptoms}

**Please provide a detailed analysis including:**

1. **Disease Identification:**
   - Most likely disease(s) based on symptoms
   - Scientific name of the pathogen
   - Confidence level in diagnosis
   - Differential diagnosis (other possible diseases)

2. **Disease Characteristics:**
   - Pathogen type (fungal, bacterial, viral, etc.)
   - Disease cycle and spread mechanism
   - Favorable environmental conditions
   - Severity assessment

3. **Management Recommendations:**
   - Immediate action steps
   - Cultural control methods
   - Chemical control options (if necessary)
   - Biological control alternatives
   - Integrated management approach

4. **Prevention Strategies:**
   - Future prevention measures
   - Resistant varieties (if available)
   - Cultural practices to reduce risk
   - Monitoring guidelines

5. **Economic Considerations:**
   - Potential yield impact if untreated
   - Cost-effectiveness of treatments
   - Long-term management costs

6. **Environmental Factors:**
   - Weather conditions that may influence disease
   - Soil factors affecting disease development
   - Neighboring crop considerations

Please provide practical, evidence-based recommendations suitable for farmers in the specified location. Include specific product names, application rates, and timing where appropriate.
""",
            "crop_planning": """
You are an expert agricultural consultant specializing in crop planning and farm management. Please provide comprehensive guidance for the following crop planning scenario.

**Planning Parameters:**
- Intended Crop: {crop_type}
- Growing Season: {season}
- Soil Type: {soil_type}

**Please provide detailed planning guidance including:**

1. **Crop Suitability Assessment:**
   - Suitability of chosen crop for given conditions
   - Expected yield potential
   - Risk factors and challenges
   - Alternative crop suggestions if needed

2. **Pre-Planting Preparation:**
   - Land preparation requirements
   - Soil amendments needed
   - Optimal planting time
   - Seed/planting material selection

3. **Cultivation Schedule:**
   - Detailed timeline from planting to harvest
   - Key growth stages and milestones
   - Critical management periods
   - Seasonal activity calendar

4. **Input Requirements:**
   - Fertilizer recommendations (type, quantity, timing)
   - Irrigation planning and water requirements
   - Pest and disease management schedule
   - Labor requirements

5. **Management Practices:**
   - Planting density and spacing
   - Intercultural operations
   - Harvesting guidelines
   - Post-harvest handling

6. **Economic Planning:**
   - Estimated input costs
   - Expected returns
   - Market considerations
   - Risk management strategies

7. **Sustainability Considerations:**
   - Crop rotation recommendations
   - Soil health maintenance
   - Environmental impact minimization
   - Organic/sustainable alternatives

Please provide practical, location-specific recommendations that consider local climate, market conditions, and farming practices.
""",
            "weather_advisory": """
You are an expert agricultural meteorologist providing weather-based farming guidance. Please analyze the current weather conditions and forecast to provide actionable agricultural advice.

**Weather Information:**
- Location: {location}
- Current Conditions: {current_weather}
- Forecast: {forecast}

**Please provide comprehensive weather advisory including:**

1. **Current Conditions Analysis:**
   - Impact of current weather on crop growth
   - Immediate risks or opportunities
   - Field work suitability
   - Irrigation needs assessment

2. **Short-term Forecast Impact (1-7 days):**
   - Expected weather changes
   - Agricultural implications
   - Recommended immediate actions
   - Field operation timing

3. **Medium-term Outlook (1-4 weeks):**
   - Seasonal weather trends
   - Crop development implications
   - Planning considerations
   - Risk preparation

4. **Crop-Specific Recommendations:**
   - Impact on different growth stages
   - Variety-specific considerations
   - Management adjustments needed
   - Harvest timing implications

5. **Field Operations Guidance:**
   - Optimal timing for planting/sowing
   - Spraying and fertilizer application windows
   - Harvesting conditions
   - Equipment operation suitability

6. **Risk Management:**
   - Weather-related risks (drought, flood, frost, heat)
   - Mitigation strategies
   - Contingency planning
   - Insurance considerations

7. **Water Management:**
   - Irrigation scheduling
   - Water conservation strategies
   - Drainage requirements
   - Soil moisture management

Please provide specific, actionable recommendations that farmers can implement based on the weather conditions and forecast.
""",
            "soil_analysis": """
You are an expert soil scientist and agricultural consultant specializing in soil fertility and crop nutrition. Please analyze the provided soil data and provide comprehensive recommendations.

**Soil Information:**
- Location: {location}
- Soil Analysis Data: {soil_data}
- Planned Crops: {crop_plans}

**Please provide detailed soil analysis and recommendations including:**

1. **Soil Health Assessment:**
   - Overall soil fertility status
   - Nutrient availability analysis
   - Physical properties evaluation
   - Chemical properties assessment
   - Biological activity indicators

2. **Nutrient Management:**
   - Macronutrient (NPK) recommendations
   - Micronutrient requirements
   - Organic matter status and needs
   - pH management strategies
   - Fertilizer recommendations (type, rate, timing)

3. **Soil Physical Properties:**
   - Texture and structure analysis
   - Drainage characteristics
   - Compaction assessment
   - Water holding capacity
   - Tillage recommendations

4. **Crop-Specific Recommendations:**
   - Soil suitability for planned crops
   - Variety selection based on soil conditions
   - Specific nutrient requirements
   - Growth optimization strategies

5. **Soil Improvement Strategies:**
   - Short-term improvement measures
   - Long-term soil building practices
   - Organic matter enhancement
   - Soil conservation methods

6. **Management Practices:**
   - Crop rotation recommendations
   - Cover cropping strategies
   - Irrigation management
   - Erosion control measures

7. **Monitoring and Testing:**
   - Follow-up soil testing schedule
   - Key parameters to monitor
   - Seasonal adjustments
   - Record keeping recommendations

8. **Economic Considerations:**
   - Cost-effective improvement strategies
   - Return on investment for soil amendments
   - Budget planning for soil management
   - Sustainable practices

Please provide practical, science-based recommendations that consider local conditions, crop requirements, and economic feasibility.
""",
            "general_agricultural_guidance": """
You are an expert agricultural extension officer providing comprehensive farming guidance. Please address the farmer's query with practical, evidence-based recommendations.

**Query Context:**
- Farmer's Question: {query}
- Location: {location}
- Crop/Farming System: {farming_context}

**Please provide comprehensive guidance including:**

1. **Direct Response:**
   - Clear answer to the specific question
   - Explanation of underlying principles
   - Practical implementation steps

2. **Technical Information:**
   - Scientific basis for recommendations
   - Best practices and standards
   - Common mistakes to avoid

3. **Local Considerations:**
   - Regional adaptations needed
   - Local resource availability
   - Climate and soil considerations

4. **Implementation Guidance:**
   - Step-by-step instructions
   - Timeline and scheduling
   - Resource requirements
   - Cost considerations

5. **Risk Management:**
   - Potential challenges
   - Mitigation strategies
   - Alternative approaches
   - Contingency planning

6. **Follow-up Actions:**
   - Monitoring requirements
   - Success indicators
   - Adjustment strategies
   - When to seek additional help

Please provide practical, actionable advice that considers the farmer's specific context and local conditions.
""",
        }
