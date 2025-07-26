"""
Tool Registry and Handler for Agricultural Assistant

Central registry for all tools and unified function call handling.
"""

import logging
from typing import Dict, Any, List, Callable
from google.genai import types

from .search import google_search, SEARCH_TOOL_DECLARATION
from .weather import (
    get_weather_by_location,
    get_weather_by_coordinates,
    WEATHER_LOCATION_TOOL_DECLARATION,
    WEATHER_COORDINATES_TOOL_DECLARATION,
)
from .crop_analysis import analyze_crop_image_and_search, CROP_ANALYSIS_TOOL_DECLARATION
from .soil_analysis import get_soilgrids_data, SOIL_ANALYSIS_TOOL_DECLARATION


class ToolRegistry:
    """Registry for all agricultural AI tools."""

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._declarations: List[Dict[str, Any]] = []
        self._register_tools()

    def _register_tools(self):
        """Register all available tools."""
        # Search tools
        self.register_tool("google_search", google_search, SEARCH_TOOL_DECLARATION)

        # Weather tools
        self.register_tool(
            "get_weather_by_location",
            get_weather_by_location,
            WEATHER_LOCATION_TOOL_DECLARATION,
        )
        self.register_tool(
            "get_weather_by_coordinates",
            get_weather_by_coordinates,
            WEATHER_COORDINATES_TOOL_DECLARATION,
        )

        # Crop analysis tools
        self.register_tool(
            "analyze_crop_image_and_search",
            analyze_crop_image_and_search,
            CROP_ANALYSIS_TOOL_DECLARATION,
        )

        # Soil analysis tools
        self.register_tool(
            "get_soilgrids_data", get_soilgrids_data, SOIL_ANALYSIS_TOOL_DECLARATION
        )

    def register_tool(self, name: str, function: Callable, declaration: Dict[str, Any]):
        """
        Register a new tool.

        Args:
            name (str): Tool name
            function (Callable): Tool function
            declaration (Dict[str, Any]): Tool declaration for Gemini AI
        """
        self._tools[name] = function
        self._declarations.append(declaration)
        logging.info(f"Registered tool: {name}")

    def get_tool(self, name: str) -> Callable:
        """
        Get a tool function by name.

        Args:
            name (str): Tool name

        Returns:
            Callable: Tool function

        Raises:
            KeyError: If tool not found
        """
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found in registry")
        return self._tools[name]

    def get_declarations(self) -> List[Dict[str, Any]]:
        """
        Get all tool declarations for Gemini AI.

        Returns:
            List[Dict[str, Any]]: List of tool declarations
        """
        return self._declarations.copy()

    def get_tools_config(self) -> List[Dict[str, Any]]:
        """
        Get tools configuration for Gemini AI.

        Returns:
            List[Dict[str, Any]]: Tools configuration
        """
        return [{"function_declarations": self._declarations}]

    def list_tools(self) -> List[str]:
        """
        List all registered tool names.

        Returns:
            List[str]: List of tool names
        """
        return list(self._tools.keys())


# Global tool registry instance
_tool_registry = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    """
    Get the global tool registry instance.

    Returns:
        ToolRegistry: Global tool registry
    """
    return _tool_registry


async def handle_function_call(function_call) -> types.FunctionResponse:
    """
    Handle function calls from Gemini AI and return responses.

    Args:
        function_call: Function call from Gemini AI

    Returns:
        types.FunctionResponse: Function response for Gemini AI
    """
    function_name = function_call.name
    args = function_call.args

    try:
        # Get the tool function from registry
        tool_function = _tool_registry.get_tool(function_name)

        # Call the appropriate tool function
        if function_name == "google_search":
            result = await tool_function(args.get("query", ""))
        elif function_name == "analyze_crop_image_and_search":
            result = await tool_function(
                args.get("image_input", ""),
                args.get("farmer_query", ""),
                args.get("include_visual_search", True),
            )
        elif function_name == "get_weather_by_location":
            result = await tool_function(args.get("city", ""))
        elif function_name == "get_weather_by_coordinates":
            result = await tool_function(args.get("lat", 0), args.get("lon", 0))
        elif function_name == "get_soilgrids_data":
            result = await tool_function(args.get("lat", 0), args.get("lon", 0))
        else:
            result = {
                "status": "error",
                "error_message": f"Unknown function: {function_name}",
            }

        logging.info(f"Successfully executed tool: {function_name}")
        return types.FunctionResponse(
            id=function_call.id, name=function_call.name, response=result
        )

    except KeyError as e:
        logging.error(f"Tool not found: {function_name}")
        return types.FunctionResponse(
            id=function_call.id,
            name=function_call.name,
            response={"status": "error", "error_message": str(e)},
        )
    except Exception as e:
        logging.error(f"Error executing tool {function_name}: {str(e)}")
        return types.FunctionResponse(
            id=function_call.id,
            name=function_call.name,
            response={"status": "error", "error_message": str(e)},
        )


def get_system_instruction() -> str:
    """
    Get the system instruction for the agricultural assistant.

    Returns:
        str: System instruction text
    """
    return """You are an expert agricultural assistant with access to Google Search, Weather, and Soil Data APIs. 
    You can help farmers with:
    - Crop disease identification and treatment recommendations
    - Weather information for farming decisions
    - Soil property analysis for crop planning
    - General agricultural research and advice
    
    When users provide images of crops, analyze them for diseases and provide actionable recommendations.
    Always provide practical, evidence-based advice. Be concise but thorough in your responses.
    
    When speaking (in voice mode), use a friendly, knowledgeable tone and speak clearly. 
    Avoid overly technical jargon when possible, but be precise about agricultural recommendations."""
