"""
Gemini HTTP Streaming Service for Real-time Agricultural Assistant

Provides real-time streaming AI assistance using HTTP Server-Sent Events (SSE)
with JWT authentication and integrated agricultural tools.
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional, AsyncGenerator
from google import genai
from google.genai import types
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..config.settings import settings
from ..config.database import get_db
from ..models.chat import ChatHistory
from ..models.user import User
from ..utils.auth import get_user_from_token
from ..tools.registry import get_tool_registry, handle_function_call


class GeminiStreamingService:
    """Service for HTTP streaming Gemini Live interactions with agricultural tools."""

    def __init__(self):
        # Configure the client with API key
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required for Gemini streaming service")

        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_LIVE_MODEL
        self.tool_registry = get_tool_registry()

    def _get_system_instruction(
        self, farmer_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Get comprehensive system instruction for agricultural assistant with optional farmer personalization."""
        base_instruction = """You are Namma Krushi AI, an expert agricultural assistant specifically designed for Karnataka farmers. 

You have access to comprehensive tools for:
- Google Search and Exa AI Search for agricultural research and advice
- Weather information (by location and coordinates) for farming decisions
- Soil property analysis using SoilGrids API for crop planning
- Crop disease identification and treatment recommendations using Google Vision
- Crop management (create, update, track crops and their stages)
- Daily farming log management (activities, weather, costs, observations)
- Sales tracking and analytics (record sales, track revenue, analyze performance)
- Government scheme search for subsidies and programs

Your capabilities include:
1. **Crop Management**: Help farmers track their crops, stages, health scores, and harvest planning
2. **Daily Farming Logs**: Record daily activities, weather conditions, inputs used, and observations
3. **Sales Analytics**: Track sales, calculate profits, analyze market performance
4. **Disease Diagnosis**: Analyze crop images to identify diseases and recommend treatments
5. **Weather Guidance**: Provide weather-based farming recommendations
6. **Soil Analysis**: Analyze soil properties and recommend suitable crops and amendments
7. **Government Schemes**: Search for and recommend relevant government schemes and subsidies
8. **Market Research**: Search for current prices, best practices, and agricultural news

Communication Style:
- Respond in a mix of Kannada and English as appropriate for Karnataka farmers
- Be practical, actionable, and specific to Karnataka's agricultural conditions
- Consider the current season and local farming practices
- Provide step-by-step guidance when needed
- Be encouraging and supportive
- Use simple language that farmers can understand
- Include cost-effective solutions
- Reference government schemes when applicable

When farmers ask questions:
1. Use appropriate tools to gather current information
2. Provide evidence-based, practical advice
3. Consider local conditions and traditional practices
4. Suggest follow-up actions or record-keeping when relevant
5. Offer to help track progress through crop/log management tools

Always be helpful, accurate, and focused on improving farming outcomes for Karnataka farmers."""

        # Add personalized information if farmer data is available
        if farmer_data:
            personalized_section = self._create_personalized_section(farmer_data)
            if personalized_section:
                base_instruction += f"\n\n{personalized_section}"

        return base_instruction

    def _create_personalized_section(self, farmer_data: Dict[str, Any]) -> str:
        """Create personalized section of system prompt based on farmer data."""
        sections = []

        # Farmer profile information
        if farmer_data.get("profile"):
            profile = farmer_data["profile"]
            sections.append("## FARMER PROFILE CONTEXT:")

            if profile.get("farmer_name"):
                sections.append(f"- Farmer Name: {profile['farmer_name']}")

            if profile.get("preferred_language"):
                sections.append(
                    f"- Preferred Language: {profile['preferred_language']}"
                )

            if profile.get("total_land_size_acres"):
                sections.append(
                    f"- Total Land: {profile['total_land_size_acres']} acres"
                )

            if profile.get("land_ownership_type"):
                sections.append(f"- Land Ownership: {profile['land_ownership_type']}")

            if profile.get("irrigation_method"):
                sections.append(f"- Irrigation Method: {profile['irrigation_method']}")

            if profile.get("primary_crops"):
                crops_str = (
                    ", ".join(profile["primary_crops"])
                    if isinstance(profile["primary_crops"], list)
                    else str(profile["primary_crops"])
                )
                sections.append(f"- Primary Crops: {crops_str}")

            if profile.get("major_challenges"):
                challenges_str = (
                    ", ".join(profile["major_challenges"])
                    if isinstance(profile["major_challenges"], list)
                    else str(profile["major_challenges"])
                )
                sections.append(f"- Major Challenges: {challenges_str}")

        # Current crops information
        if farmer_data.get("current_crops"):
            sections.append("\n## CURRENT CROPS:")
            for crop in farmer_data["current_crops"][:5]:  # Limit to 5 crops
                crop_info = f"- {crop.get('crop_name', 'Unknown')} ({crop.get('total_area_acres', 0)} acres)"
                if crop.get("crop_stage"):
                    crop_info += f" - Stage: {crop['crop_stage']}"
                if crop.get("current_crop"):
                    crop_info += f" - Type: {crop['current_crop']}"
                if crop.get("planting_date"):
                    crop_info += f" - Planted: {crop['planting_date']}"
                sections.append(crop_info)

        # Recent activities
        if farmer_data.get("recent_logs"):
            sections.append("\n## RECENT FARMING ACTIVITIES:")
            for log in farmer_data["recent_logs"][:3]:  # Limit to 3 recent logs
                log_info = f"- {log.get('log_date', 'Unknown date')}: {log.get('activity_type', 'Activity')} - {log.get('description', 'No description')}"
                sections.append(log_info)

        # Sales performance
        if farmer_data.get("recent_sales"):
            sections.append("\n## RECENT SALES:")
            total_revenue = sum(
                sale.get("total_amount", 0) for sale in farmer_data["recent_sales"]
            )
            sections.append(f"- Recent sales revenue: ₹{total_revenue:,.2f}")
            for sale in farmer_data["recent_sales"][:3]:  # Limit to 3 recent sales
                sale_info = f"- {sale.get('sale_date', 'Unknown')}: {sale.get('crop_type', 'Unknown crop')} - ₹{sale.get('total_amount', 0):,.2f}"
                sections.append(sale_info)

        if sections:
            sections.append("\n## PERSONALIZATION INSTRUCTIONS:")
            sections.append(
                "- Use this farmer's specific context when providing advice"
            )
            sections.append(
                "- Reference their current crops and activities when relevant"
            )
            sections.append(
                "- Consider their land size and farming methods in recommendations"
            )
            sections.append(
                "- Acknowledge their challenges and provide targeted solutions"
            )
            sections.append("- Suggest improvements based on their current practices")

        return "\n".join(sections)

    def get_farmer_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Fetch comprehensive farmer data from database."""
        if not user_id:
            return None

        try:
            from ..models.farmer_profile import FarmerProfile
            from ..models.crop import Crop
            from ..models.daily_log import DailyLog
            from ..models.sale import Sale

            db = next(get_db())

            # Get farmer profile
            farmer_profile = (
                db.query(FarmerProfile).filter(FarmerProfile.user_id == user_id).first()
            )

            # Get current crops
            current_crops = (
                db.query(Crop)
                .filter(Crop.user_id == user_id)
                .order_by(Crop.created_at.desc())
                .limit(10)
                .all()
            )

            # Get recent daily logs
            recent_logs = (
                db.query(DailyLog)
                .filter(DailyLog.user_id == user_id)
                .order_by(DailyLog.log_date.desc())
                .limit(5)
                .all()
            )

            # Get recent sales
            recent_sales = (
                db.query(Sale)
                .filter(Sale.user_id == user_id)
                .order_by(Sale.sale_date.desc())
                .limit(5)
                .all()
            )

            farmer_data = {
                "profile": None,
                "current_crops": [],
                "recent_logs": [],
                "recent_sales": [],
            }

            # Convert farmer profile to dict
            if farmer_profile:
                farmer_data["profile"] = {
                    "farmer_name": farmer_profile.farmer_name,
                    "preferred_language": farmer_profile.preferred_language,
                    "total_land_size_acres": farmer_profile.total_land_size_acres,
                    "cultivable_land_acres": farmer_profile.cultivable_land_acres,
                    "land_ownership_type": farmer_profile.land_ownership_type,
                    "irrigation_method": farmer_profile.irrigation_method,
                    "primary_crops": farmer_profile.primary_crops,
                    "major_challenges": farmer_profile.major_challenges,
                    "farming_goals": farmer_profile.farming_goals,
                    "profile_completion_percentage": farmer_profile.profile_completion_percentage,
                }

            # Convert crops to dict
            farmer_data["current_crops"] = [
                {
                    "id": crop.id,
                    "crop_name": crop.crop_name,
                    "current_crop": crop.current_crop,
                    "crop_variety": crop.crop_variety,
                    "total_area_acres": crop.total_area_acres,
                    "crop_stage": crop.crop_stage,
                    "crop_health_score": crop.crop_health_score,
                    "planting_date": crop.planting_date.isoformat()
                    if crop.planting_date
                    else None,
                    "expected_harvest_date": crop.expected_harvest_date.isoformat()
                    if crop.expected_harvest_date
                    else None,
                    "soil_type": crop.soil_type,
                    "irrigation_type": crop.irrigation_type,
                }
                for crop in current_crops
            ]

            # Convert logs to dict
            farmer_data["recent_logs"] = [
                {
                    "id": log.id,
                    "log_date": log.log_date.isoformat() if log.log_date else None,
                    "activity_type": log.activity_type,
                    "description": log.description,
                    "weather_condition": log.weather_condition,
                    "cost_incurred": log.cost_incurred,
                    "observations": log.observations,
                }
                for log in recent_logs
            ]

            # Convert sales to dict
            farmer_data["recent_sales"] = [
                {
                    "id": sale.id,
                    "sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
                    "crop_type": sale.crop_type,
                    "crop_variety": sale.crop_variety,
                    "quantity_kg": sale.quantity_kg,
                    "price_per_kg": sale.price_per_kg,
                    "total_amount": sale.total_amount,
                    "buyer_type": sale.buyer_type,
                    "market_location": sale.market_location,
                }
                for sale in recent_sales
            ]

            return farmer_data

        except Exception as e:
            logging.error(f"Failed to fetch farmer data for user {user_id}: {str(e)}")
            return None
        finally:
            db.close()

    async def stream_chat_response(
        self, message: str, user: User, farmer_data: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat response using Server-Sent Events.

        Args:
            message (str): User message
            user (User): Authenticated user
            farmer_data (Dict[str, Any], optional): Farmer profile data

        Yields:
            str: SSE formatted response chunks
        """
        try:
            logging.info(f"Starting streaming chat for user {user.id}: {message}")

            # Setup configuration with personalized system prompt
            config = {
                "response_modalities": ["TEXT"],
                "tools": self.tool_registry.get_tools_config(),
                "system_instruction": self._get_system_instruction(farmer_data),
            }

            # Send initial connection message
            if farmer_data and farmer_data.get("profile"):
                profile = farmer_data["profile"]
                farmer_name = profile.get("farmer_name", user.email.split("@")[0])
                welcome_message = f"ನಮಸ್ಕಾರ {farmer_name}! I can see your farming profile and will provide personalized advice."
            else:
                welcome_message = "Connected to Namma Krushi AI! I can help with crops, weather, soil analysis, and farming advice."

            yield f"data: {json.dumps({'type': 'system', 'content': welcome_message})}\n\n"

            # Initialize variables for chat history
            current_ai_response = ""

            async with self.client.aio.live.connect(
                model=self.model, config=config
            ) as session:
                # Send user message to GenAI
                await session.send_client_content(turns={"parts": [{"text": message}]})

                # Process responses and stream back to client
                async for chunk in session.receive():
                    if chunk.server_content:
                        if chunk.text is not None:
                            # Accumulate AI response for saving to database
                            current_ai_response += chunk.text

                            # Stream text response to client
                            yield f"data: {json.dumps({'type': 'response', 'content': chunk.text})}\n\n"

                    elif chunk.tool_call:
                        # Notify client that functions are being called
                        function_names = [
                            fc.name for fc in chunk.tool_call.function_calls
                        ]
                        tools_message = f"🔧 Using tools: {', '.join(function_names)}"
                        yield f"data: {json.dumps({'type': 'function_call', 'functions': function_names, 'message': tools_message})}\n\n"
                        # Execute function calls using our tool registry
                        function_responses = []
                        for fc in chunk.tool_call.function_calls:
                            try:
                                # Use our existing handle_function_call but convert response format
                                response_dict = await handle_function_call(fc)

                                # Convert our dict response to types.FunctionResponse
                                function_response = types.FunctionResponse(
                                    id=response_dict["id"],
                                    name=response_dict["name"],
                                    response=response_dict["response"],
                                )
                                function_responses.append(function_response)

                                logging.info(f"Executed tool: {fc.name}")
                            except Exception as e:
                                logging.error(
                                    f"Error executing tool {fc.name}: {str(e)}"
                                )
                                # Create error response
                                error_response = types.FunctionResponse(
                                    id=fc.id,
                                    name=fc.name,
                                    response={
                                        "status": "error",
                                        "error_message": str(e),
                                    },
                                )
                                function_responses.append(error_response)

                        # Send tool responses back to Gemini
                        await session.send_tool_response(
                            function_responses=function_responses
                        )

                # Save chat history after response is complete
                if message and current_ai_response:
                    self.save_chat_history(user.id, message, current_ai_response)

                # Send completion message
                yield f"data: {json.dumps({'type': 'complete', 'content': 'Response completed'})}\n\n"

        except Exception as e:
            logging.error(f"Streaming chat error: {str(e)}")
            error_message = f"Chat error: {str(e)}"
            yield f"data: {json.dumps({'type': 'error', 'content': error_message})}\n\n"

    def save_chat_history(self, user_id: int, user_message: str, ai_response: str):
        """Save chat history to database."""
        if not user_id:
            return

        try:
            db = next(get_db())

            # Determine message type based on content
            message_type = self._determine_message_type(user_message)

            chat_entry = ChatHistory(
                user_id=user_id,
                user_message=user_message,
                ai_response=ai_response,
                message_type=message_type,
                language="en",  # Default to English, could be enhanced to detect language
                is_voice_message=False,  # Always False since we removed voice
                follow_up_needed=False,
            )

            db.add(chat_entry)
            db.commit()
            db.refresh(chat_entry)

            logging.info(f"Saved chat history for user {user_id}")

        except Exception as e:
            logging.error(f"Failed to save chat history: {str(e)}")
        finally:
            db.close()

    def _determine_message_type(self, message: str) -> str:
        """Determine the type of chat message based on content."""
        message_lower = message.lower()

        # Keywords for different message types
        weather_keywords = ["weather", "rain", "temperature", "climate", "ಹವಾಮಾನ", "ಮಳೆ"]
        disease_keywords = ["disease", "pest", "sick", "problem", "ರೋಗ", "ಕೀಟ"]
        market_keywords = ["price", "sell", "market", "buyer", "ಬೆಲೆ", "ಮಾರುಕಟ್ಟೆ"]
        farm_keywords = ["farm", "crop", "plant", "harvest", "ಬೆಳೆ", "ಕೃಷಿ"]
        scheme_keywords = ["scheme", "subsidy", "government", "yojana", "ಯೋಜನೆ", "ಸಬ್ಸಿಡಿ"]

        if any(keyword in message_lower for keyword in weather_keywords):
            return "weather"
        elif any(keyword in message_lower for keyword in disease_keywords):
            return "disease"
        elif any(keyword in message_lower for keyword in market_keywords):
            return "market"
        elif any(keyword in message_lower for keyword in scheme_keywords):
            return "scheme"
        elif any(keyword in message_lower for keyword in farm_keywords):
            return "farm_specific"
        else:
            return "general"

    def get_available_tools(self) -> Dict[str, Any]:
        """Get information about available tools."""
        tools = self.tool_registry.list_tools()
        return {
            "total_tools": len(tools),
            "tools": tools,
            "categories": {
                "search": ["google_search", "exa_search", "exa_search_agricultural"],
                "schemes": ["search_government_schemes"],
                "weather": ["get_weather_by_location", "get_weather_by_coordinates"],
                "soil": ["get_soilgrids_data"],
                "crop_analysis": ["analyze_crop_image_and_search"],
                "crop_management": [
                    "create_crop_tool",
                    "update_crop_tool",
                    "get_crops_tool",
                ],
                "daily_logs": [
                    "create_daily_log_tool",
                    "update_daily_log_tool",
                    "get_daily_logs_tool",
                ],
                "sales": [
                    "create_sale_tool",
                    "update_sale_tool",
                    "get_sales_tool",
                    "get_sales_analytics_tool",
                ],
            },
        }


# Global service instance (lazy initialization)
_gemini_streaming_service = None


def get_gemini_streaming_service() -> GeminiStreamingService:
    """Get or create the global Gemini streaming service instance."""
    global _gemini_streaming_service
    if _gemini_streaming_service is None:
        _gemini_streaming_service = GeminiStreamingService()
    return _gemini_streaming_service
