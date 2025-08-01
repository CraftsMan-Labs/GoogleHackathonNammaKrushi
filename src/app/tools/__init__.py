"""
Agricultural AI Tools Module

This module contains all the tool implementations for the agricultural AI assistant.
Each tool is organized in separate modules for better maintainability.

Usage:
    from src.app.tools import get_tool_registry, handle_function_call
    
    # Get tool registry for Gemini AI configuration
    registry = get_tool_registry()
    tools_config = registry.get_tools_config()
    
    # Handle function calls from Gemini AI
    response = await handle_function_call(function_call)
"""

from .search import google_search
from .weather import get_weather_by_location, get_weather_by_coordinates
from .crop_analysis import analyze_crop_image_and_search
from .soil_analysis import get_soilgrids_data
from .crop_management import create_crop_tool, update_crop_tool, get_crops_tool
from .daily_log_management import (
    create_daily_log_tool,
    update_daily_log_tool,
    get_daily_logs_tool,
)
from .sales_management import (
    create_sale_tool,
    update_sale_tool,
    get_sales_tool,
    get_sales_analytics_tool,
)
from .registry import get_tool_registry, handle_function_call

__all__ = [
    "google_search",
    "get_weather_by_location",
    "get_weather_by_coordinates",
    "analyze_crop_image_and_search",
    "get_soilgrids_data",
    "create_crop_tool",
    "update_crop_tool",
    "get_crops_tool",
    "create_daily_log_tool",
    "update_daily_log_tool",
    "get_daily_logs_tool",
    "create_sale_tool",
    "update_sale_tool",
    "get_sales_tool",
    "get_sales_analytics_tool",
    "get_tool_registry",
    "handle_function_call",
]
