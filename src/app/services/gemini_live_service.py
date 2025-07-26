"""
Gemini Live Service for Real-time Agricultural Assistant

Provides real-time streaming AI assistance using Google's Gemini Live API
with integrated agricultural tools.
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from ..config.settings import settings
from ..config.database import get_db
from ..models.chat import ChatHistory
from ..tools.registry import get_tool_registry, handle_function_call


class GeminiLiveService:
    """Service for real-time Gemini Live interactions with agricultural tools."""

    def __init__(self):
        # Configure the client with API key
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required for Gemini Live service")

        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_LIVE_MODEL
        self.tool_registry = get_tool_registry()

        # Initialize chat history tracking variables
        self.current_user_message = None
        self.current_user_id = None
        self.current_ai_response = ""

        self._setup_config()

    def _setup_config(self):
        """Setup Gemini Live configuration with all agricultural tools for text-only chat."""
        self.config = {
            "response_modalities": ["TEXT"],
            "tools": self.tool_registry.get_tools_config(),
            "system_instruction": self._get_system_instruction(),
        }

    def _get_system_instruction(self) -> str:
        """Get comprehensive system instruction for agricultural assistant."""
        return """You are Namma Krushi AI, an expert agricultural assistant specifically designed for Karnataka farmers. 

You have access to comprehensive tools for:
- Google Search for agricultural research and advice
- Weather information (by location and coordinates) for farming decisions
- Soil property analysis using SoilGrids API for crop planning
- Crop disease identification and treatment recommendations using Google Vision
- Crop management (create, update, track crops and their stages)
- Daily farming log management (activities, weather, costs, observations)
- Sales tracking and analytics (record sales, track revenue, analyze performance)

Your capabilities include:
1. **Crop Management**: Help farmers track their crops, stages, health scores, and harvest planning
2. **Daily Farming Logs**: Record daily activities, weather conditions, inputs used, and observations
3. **Sales Analytics**: Track sales, calculate profits, analyze market performance
4. **Disease Diagnosis**: Analyze crop images to identify diseases and recommend treatments
5. **Weather Guidance**: Provide weather-based farming recommendations
6. **Soil Analysis**: Analyze soil properties and recommend suitable crops and amendments
7. **Market Research**: Search for current prices, best practices, and agricultural news

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

        if any(keyword in message_lower for keyword in weather_keywords):
            return "weather"
        elif any(keyword in message_lower for keyword in disease_keywords):
            return "disease"
        elif any(keyword in message_lower for keyword in market_keywords):
            return "market"
        elif any(keyword in message_lower for keyword in farm_keywords):
            return "farm_specific"
        else:
            return "general"

    async def handle_websocket_session(self, websocket, user_id: int = None):
        """Handle a complete WebSocket session with Gemini Live and save chat history."""
        await websocket.accept()

        try:
            async with self.client.aio.live.connect(
                model=self.model, config=self.config
            ) as session:
                # Send welcome message
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "system",
                            "content": "Connected to Namma Krushi AI! I can help with crops, weather, soil analysis, and farming advice.",
                        }
                    )
                )

                while True:
                    try:
                        # Receive message from client
                        data = await websocket.receive_text()
                        message_data = json.loads(data)
                        user_message = message_data.get("message", "")

                        if not user_message:
                            continue

                        # Store message for history tracking
                        self.current_user_message = user_message
                        self.current_user_id = user_id
                        self.current_ai_response = ""

                        # Send user message to GenAI
                        await session.send_client_content(
                            turns={"parts": [{"text": user_message}]}
                        )

                        # Process responses and stream back to client
                        async for chunk in session.receive():
                            if chunk.server_content:
                                if chunk.text is not None:
                                    # Accumulate AI response for saving to database
                                    self.current_ai_response += chunk.text

                                    # Stream text response to client
                                    await websocket.send_text(
                                        json.dumps(
                                            {"type": "response", "content": chunk.text}
                                        )
                                    )

                            elif chunk.tool_call:
                                # Notify client that functions are being called
                                function_names = [
                                    fc.name for fc in chunk.tool_call.function_calls
                                ]
                                await websocket.send_text(
                                    json.dumps(
                                        {
                                            "type": "function_call",
                                            "functions": function_names,
                                            "message": f"🔧 Using tools: {', '.join(function_names)}",
                                        }
                                    )
                                )

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
                        if self.current_user_message and self.current_ai_response:
                            self.save_chat_history(
                                self.current_user_id,
                                self.current_user_message,
                                self.current_ai_response,
                            )
                            # Clear the stored message
                            self.current_user_message = None
                            self.current_user_id = None
                            self.current_ai_response = ""

                    except Exception as e:
                        logging.error(f"Error in message processing: {str(e)}")
                        await websocket.send_text(
                            json.dumps({"type": "error", "content": str(e)})
                        )

        except Exception as e:
            logging.error(f"WebSocket session error: {str(e)}")
            try:
                await websocket.send_text(
                    json.dumps(
                        {"type": "error", "content": f"Connection error: {str(e)}"}
                    )
                )
            except:
                pass
        finally:
            try:
                await websocket.close()
            except:
                pass

    def get_available_tools(self) -> Dict[str, Any]:
        """Get information about available tools."""
        tools = self.tool_registry.list_tools()
        return {
            "total_tools": len(tools),
            "tools": tools,
            "categories": {
                "search": ["google_search"],
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
_gemini_live_service = None


def get_gemini_live_service() -> GeminiLiveService:
    """Get or create the global Gemini Live service instance."""
    global _gemini_live_service
    if _gemini_live_service is None:
        _gemini_live_service = GeminiLiveService()
    return _gemini_live_service


# For backward compatibility
gemini_live_service = None
