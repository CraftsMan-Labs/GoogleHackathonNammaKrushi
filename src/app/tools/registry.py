"""
Tool Registry and Handler for Agricultural Assistant

Central registry for all tools and unified function call handling.
"""

import logging
from typing import Dict, Any, List, Callable

from .search import google_search, SEARCH_TOOL_DECLARATION
from .exa_search import (
    exa_search,
    exa_search_agricultural,
    EXA_SEARCH_TOOL_DECLARATION,
    EXA_AGRICULTURAL_SEARCH_TOOL_DECLARATION,
)
from .scheme_search import (
    search_government_schemes,
    SCHEME_SEARCH_TOOL_DECLARATION,
)
from .weather import (
    get_weather_by_location,
    get_weather_by_coordinates,
    WEATHER_LOCATION_TOOL_DECLARATION,
    WEATHER_COORDINATES_TOOL_DECLARATION,
)
from .crop_analysis import analyze_crop_image_and_search, CROP_ANALYSIS_TOOL_DECLARATION
from .soil_analysis import get_soilgrids_data, SOIL_ANALYSIS_TOOL_DECLARATION
from .crop_management import (
    create_crop_tool,
    update_crop_tool,
    get_crops_tool,
    CREATE_CROP_TOOL_DECLARATION,
    UPDATE_CROP_TOOL_DECLARATION,
    GET_CROPS_TOOL_DECLARATION,
)
from .daily_log_management import (
    create_daily_log_tool,
    update_daily_log_tool,
    get_daily_logs_tool,
    CREATE_DAILY_LOG_TOOL_DECLARATION,
    UPDATE_DAILY_LOG_TOOL_DECLARATION,
    GET_DAILY_LOGS_TOOL_DECLARATION,
)
from .sales_management import (
    create_sale_tool,
    update_sale_tool,
    get_sales_tool,
    get_sales_analytics_tool,
    CREATE_SALE_TOOL_DECLARATION,
    UPDATE_SALE_TOOL_DECLARATION,
    GET_SALES_TOOL_DECLARATION,
    GET_SALES_ANALYTICS_TOOL_DECLARATION,
)


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
        self.register_tool("exa_search", exa_search, EXA_SEARCH_TOOL_DECLARATION)
        self.register_tool(
            "exa_search_agricultural",
            exa_search_agricultural,
            EXA_AGRICULTURAL_SEARCH_TOOL_DECLARATION,
        )
        self.register_tool(
            "search_government_schemes",
            search_government_schemes,
            SCHEME_SEARCH_TOOL_DECLARATION,
        )

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

        # Crop management tools
        self.register_tool(
            "create_crop_tool", create_crop_tool, CREATE_CROP_TOOL_DECLARATION
        )
        self.register_tool(
            "update_crop_tool", update_crop_tool, UPDATE_CROP_TOOL_DECLARATION
        )
        self.register_tool("get_crops_tool", get_crops_tool, GET_CROPS_TOOL_DECLARATION)

        # Daily log management tools
        self.register_tool(
            "create_daily_log_tool",
            create_daily_log_tool,
            CREATE_DAILY_LOG_TOOL_DECLARATION,
        )
        self.register_tool(
            "update_daily_log_tool",
            update_daily_log_tool,
            UPDATE_DAILY_LOG_TOOL_DECLARATION,
        )
        self.register_tool(
            "get_daily_logs_tool", get_daily_logs_tool, GET_DAILY_LOGS_TOOL_DECLARATION
        )

        # Sales management tools
        self.register_tool(
            "create_sale_tool", create_sale_tool, CREATE_SALE_TOOL_DECLARATION
        )
        self.register_tool(
            "update_sale_tool", update_sale_tool, UPDATE_SALE_TOOL_DECLARATION
        )
        self.register_tool("get_sales_tool", get_sales_tool, GET_SALES_TOOL_DECLARATION)
        self.register_tool(
            "get_sales_analytics_tool",
            get_sales_analytics_tool,
            GET_SALES_ANALYTICS_TOOL_DECLARATION,
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


async def handle_function_call(function_call) -> Dict[str, Any]:
    """
    Handle function calls from Gemini AI and return responses.

    Args:
        function_call: Function call from Gemini AI

    Returns:
        Dict[str, Any]: Function response for Gemini AI
    """
    function_name = function_call.name
    args = function_call.args

    try:
        # Get the tool function from registry
        tool_function = _tool_registry.get_tool(function_name)

        # Call the appropriate tool function
        if function_name == "google_search":
            result = await tool_function(args.get("query", ""))
        elif function_name == "exa_search":
            result = tool_function(
                query=args.get("query", ""),
                num_results=args.get("num_results", 10),
                include_domains=args.get("include_domains"),
                exclude_domains=args.get("exclude_domains"),
                use_autoprompt=args.get("use_autoprompt", True),
                include_text=args.get("include_text", True),
                include_highlights=args.get("include_highlights", True),
            )
        elif function_name == "exa_search_agricultural":
            result = tool_function(args.get("query", ""))
        elif function_name == "search_government_schemes":
            result = await tool_function(
                query=args.get("query", ""), max_results=args.get("max_results", 10)
            )
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

        # Crop management tools
        elif function_name == "create_crop_tool":
            result = await tool_function(
                user_id=args.get("user_id"),
                crop_name=args.get("crop_name"),
                latitude=args.get("latitude"),
                longitude=args.get("longitude"),
                total_area_acres=args.get("total_area_acres"),
                current_crop=args.get("current_crop"),
                crop_variety=args.get("crop_variety"),
                planting_date=args.get("planting_date"),
                expected_harvest_date=args.get("expected_harvest_date"),
                soil_type=args.get("soil_type"),
                irrigation_type=args.get("irrigation_type"),
                address=args.get("address"),
                village=args.get("village"),
                district=args.get("district"),
                state=args.get("state", "Karnataka"),
            )
        elif function_name == "update_crop_tool":
            result = await tool_function(
                crop_id=args.get("crop_id"),
                user_id=args.get("user_id"),
                crop_stage=args.get("crop_stage"),
                crop_health_score=args.get("crop_health_score"),
                current_crop=args.get("current_crop"),
                crop_variety=args.get("crop_variety"),
                planting_date=args.get("planting_date"),
                expected_harvest_date=args.get("expected_harvest_date"),
                total_area_acres=args.get("total_area_acres"),
                cultivable_area_acres=args.get("cultivable_area_acres"),
                soil_type=args.get("soil_type"),
                irrigation_type=args.get("irrigation_type"),
            )
        elif function_name == "get_crops_tool":
            result = await tool_function(
                user_id=args.get("user_id"),
                crop_id=args.get("crop_id"),
                current_crop=args.get("current_crop"),
                crop_stage=args.get("crop_stage"),
                limit=args.get("limit", 10),
            )

        # Daily log management tools
        elif function_name == "create_daily_log_tool":
            result = await tool_function(
                user_id=args.get("user_id"),
                crop_id=args.get("crop_id"),
                log_date=args.get("log_date"),
                activity_type=args.get("activity_type"),
                description=args.get("description"),
                weather_condition=args.get("weather_condition"),
                temperature=args.get("temperature"),
                humidity=args.get("humidity"),
                rainfall=args.get("rainfall"),
                irrigation_duration=args.get("irrigation_duration"),
                fertilizer_applied=args.get("fertilizer_applied"),
                pesticide_applied=args.get("pesticide_applied"),
                labor_hours=args.get("labor_hours"),
                cost_incurred=args.get("cost_incurred"),
                observations=args.get("observations"),
                issues_found=args.get("issues_found"),
                actions_taken=args.get("actions_taken"),
            )
        elif function_name == "update_daily_log_tool":
            result = await tool_function(
                log_id=args.get("log_id"),
                user_id=args.get("user_id"),
                activity_type=args.get("activity_type"),
                description=args.get("description"),
                weather_condition=args.get("weather_condition"),
                temperature=args.get("temperature"),
                humidity=args.get("humidity"),
                rainfall=args.get("rainfall"),
                irrigation_duration=args.get("irrigation_duration"),
                fertilizer_applied=args.get("fertilizer_applied"),
                pesticide_applied=args.get("pesticide_applied"),
                labor_hours=args.get("labor_hours"),
                cost_incurred=args.get("cost_incurred"),
                observations=args.get("observations"),
                issues_found=args.get("issues_found"),
                actions_taken=args.get("actions_taken"),
            )
        elif function_name == "get_daily_logs_tool":
            result = await tool_function(
                user_id=args.get("user_id"),
                crop_id=args.get("crop_id"),
                log_id=args.get("log_id"),
                activity_type=args.get("activity_type"),
                start_date=args.get("start_date"),
                end_date=args.get("end_date"),
                limit=args.get("limit", 20),
            )

        # Sales management tools
        elif function_name == "create_sale_tool":
            result = await tool_function(
                user_id=args.get("user_id"),
                crop_id=args.get("crop_id"),
                sale_date=args.get("sale_date"),
                crop_type=args.get("crop_type"),
                crop_variety=args.get("crop_variety"),
                quantity_kg=args.get("quantity_kg"),
                price_per_kg=args.get("price_per_kg"),
                total_amount=args.get("total_amount"),
                buyer_name=args.get("buyer_name"),
                buyer_type=args.get("buyer_type"),
                buyer_contact=args.get("buyer_contact"),
                payment_method=args.get("payment_method"),
                payment_status=args.get("payment_status", "pending"),
                transportation_cost=args.get("transportation_cost"),
                commission_paid=args.get("commission_paid"),
                quality_grade=args.get("quality_grade"),
                quality_notes=args.get("quality_notes"),
                market_location=args.get("market_location"),
                market_price_reference=args.get("market_price_reference"),
                notes=args.get("notes"),
                invoice_number=args.get("invoice_number"),
            )
        elif function_name == "update_sale_tool":
            result = await tool_function(
                sale_id=args.get("sale_id"),
                user_id=args.get("user_id"),
                crop_type=args.get("crop_type"),
                crop_variety=args.get("crop_variety"),
                quantity_kg=args.get("quantity_kg"),
                price_per_kg=args.get("price_per_kg"),
                total_amount=args.get("total_amount"),
                buyer_name=args.get("buyer_name"),
                buyer_type=args.get("buyer_type"),
                buyer_contact=args.get("buyer_contact"),
                payment_method=args.get("payment_method"),
                payment_status=args.get("payment_status"),
                transportation_cost=args.get("transportation_cost"),
                commission_paid=args.get("commission_paid"),
                quality_grade=args.get("quality_grade"),
                quality_notes=args.get("quality_notes"),
                market_location=args.get("market_location"),
                market_price_reference=args.get("market_price_reference"),
                notes=args.get("notes"),
                invoice_number=args.get("invoice_number"),
            )
        elif function_name == "get_sales_tool":
            result = await tool_function(
                user_id=args.get("user_id"),
                sale_id=args.get("sale_id"),
                crop_id=args.get("crop_id"),
                crop_type=args.get("crop_type"),
                buyer_type=args.get("buyer_type"),
                payment_status=args.get("payment_status"),
                start_date=args.get("start_date"),
                end_date=args.get("end_date"),
                limit=args.get("limit", 20),
            )
        elif function_name == "get_sales_analytics_tool":
            result = await tool_function(
                user_id=args.get("user_id"),
                crop_type=args.get("crop_type"),
                start_date=args.get("start_date"),
                end_date=args.get("end_date"),
            )

        else:
            result = {
                "status": "error",
                "error_message": f"Unknown function: {function_name}",
            }

        logging.info(f"Successfully executed tool: {function_name}")
        return {"id": function_call.id, "name": function_call.name, "response": result}

    except KeyError as e:
        logging.error(f"Tool not found: {function_name}")
        return {
            "id": function_call.id,
            "name": function_call.name,
            "response": {"status": "error", "error_message": str(e)},
        }
    except Exception as e:
        logging.error(f"Error executing tool {function_name}: {str(e)}")
        return {
            "id": function_call.id,
            "name": function_call.name,
            "response": {"status": "error", "error_message": str(e)},
        }


def get_system_instruction() -> str:
    """
    Get the system instruction for the agricultural assistant.

    Returns:
        str: System instruction text
    """
    return """You are an expert agricultural assistant with access to Google Search, Exa AI Search, Government Scheme Search, Weather, and Soil Data APIs. 
    You can help farmers with:
    - Crop disease identification and treatment recommendations
    - Weather information for farming decisions
    - Soil property analysis for crop planning
    - Government scheme and subsidy information
    - General agricultural research and advice
    - Advanced research using AI-powered search with content extraction
    
    Search Tools Available:
    - google_search: Traditional Google search for general queries
    - exa_search: Advanced AI-powered search with content extraction and highlights
    - exa_search_agricultural: Specialized search optimized for agricultural content from trusted sources
    - search_government_schemes: AI-powered search for government schemes, subsidies, and programs with structured output
    
    When users ask about government schemes, subsidies, or financial assistance, use the search_government_schemes tool 
    to provide accurate, up-to-date information about available programs.
    
    When users provide images of crops, analyze them for diseases and provide actionable recommendations.
    Always provide practical, evidence-based advice. Be concise but thorough in your responses.
    
    For research queries, prefer exa_search_agricultural for agricultural topics as it provides more comprehensive 
    content with highlights and focuses on trusted agricultural sources.
    
    When speaking (in voice mode), use a friendly, knowledgeable tone and speak clearly. 
    Avoid overly technical jargon when possible, but be precise about agricultural recommendations."""
