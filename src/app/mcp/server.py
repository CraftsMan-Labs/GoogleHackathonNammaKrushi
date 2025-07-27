"""
NammaKrushi MCP Server

Main Model Context Protocol server implementation for NammaKrushi agricultural services.
Provides zero-retention access to agricultural tools, resources, and prompts.
"""

import asyncio
import json
import logging
from typing import Any, Sequence, Dict, List, Optional
from mcp import types
from mcp.server import Server
from mcp.server.models import InitializationOptions

from .config.mcp_settings import get_mcp_config
from .security.zero_retention import get_zero_retention_proxy
from .tools.disease_analysis import DiseaseAnalysisTool
from .tools.weather_tools import WeatherAnalysisTool
from .tools.soil_tools import SoilAnalysisTool
from .tools.search_tools import GovernmentSchemesTool, AgriculturalResearchTool
from .resources.crop_calendar import CropCalendarResource
from .resources.disease_database import DiseaseDatabaseResource
from .prompts.agricultural_prompts import AgriculturalPrompts

logger = logging.getLogger(__name__)


class NammaKrushiMCPServer:
    """
    NammaKrushi Model Context Protocol Server.

    Provides agricultural AI services through the standardized MCP interface
    while maintaining zero data retention for farmer privacy.
    """

    def __init__(self):
        self.config = get_mcp_config()
        self.zero_retention_proxy = get_zero_retention_proxy()
        self.server = Server(self.config.name)

        # Initialize tool handlers
        self.disease_tool = DiseaseAnalysisTool()
        self.weather_tool = WeatherAnalysisTool()
        self.soil_tool = SoilAnalysisTool()
        self.schemes_tool = GovernmentSchemesTool()
        self.research_tool = AgriculturalResearchTool()

        # Initialize resource handlers
        self.crop_calendar = CropCalendarResource()
        self.disease_database = DiseaseDatabaseResource()

        # Initialize prompt handlers
        self.prompts = AgriculturalPrompts()

        self._setup_handlers()

    def _setup_handlers(self):
        """Setup all MCP handlers for tools, resources, and prompts."""
        self._setup_tool_handlers()
        self._setup_resource_handlers()
        self._setup_prompt_handlers()
        logger.info("NammaKrushi MCP server handlers initialized")

    def _setup_tool_handlers(self):
        """Setup tool handlers for agricultural services."""

        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List all available agricultural tools."""
            tools = []

            if "disease_analysis" in self.config.enabled_tools:
                tools.append(
                    types.Tool(
                        name="namma_krushi.disease_analysis",
                        description="Analyze crop diseases from symptoms and images with AI-powered diagnosis",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "crop_type": {
                                    "type": "string",
                                    "description": "Type of crop being analyzed (e.g., Wheat, Rice, Cotton)",
                                },
                                "symptoms_text": {
                                    "type": "string",
                                    "description": "Detailed description of observed symptoms",
                                },
                                "location": {
                                    "type": "string",
                                    "description": "Location of the crop (city, state)",
                                },
                                "image_base64": {
                                    "type": "string",
                                    "description": "Base64 encoded crop image (optional)",
                                },
                            },
                            "required": ["crop_type", "symptoms_text"],
                        },
                    )
                )

            if "weather_analysis" in self.config.enabled_tools:
                tools.append(
                    types.Tool(
                        name="namma_krushi.weather_analysis",
                        description="Get weather data and agricultural forecasts for farming decisions",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "Location for weather data (city, state)",
                                },
                                "latitude": {
                                    "type": "number",
                                    "description": "Latitude coordinate (optional)",
                                },
                                "longitude": {
                                    "type": "number",
                                    "description": "Longitude coordinate (optional)",
                                },
                            },
                            "required": ["location"],
                        },
                    )
                )

            if "soil_analysis" in self.config.enabled_tools:
                tools.append(
                    types.Tool(
                        name="namma_krushi.soil_analysis",
                        description="Analyze soil properties and get recommendations for crop planning",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "latitude": {
                                    "type": "number",
                                    "description": "Latitude coordinate",
                                },
                                "longitude": {
                                    "type": "number",
                                    "description": "Longitude coordinate",
                                },
                            },
                            "required": ["latitude", "longitude"],
                        },
                    )
                )

            if "government_schemes_search" in self.config.enabled_tools:
                tools.append(
                    types.Tool(
                        name="namma_krushi.government_schemes_search",
                        description="Search for government agricultural schemes, subsidies, and financial assistance programs",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query for schemes (e.g., 'crop insurance', 'fertilizer subsidy')",
                                },
                                "state": {
                                    "type": "string",
                                    "description": "State name (default: Karnataka)",
                                    "default": "Karnataka",
                                },
                                "max_results": {
                                    "type": "integer",
                                    "description": "Maximum number of results to return",
                                    "default": 10,
                                },
                            },
                            "required": ["query"],
                        },
                    )
                )

            if "agricultural_research_search" in self.config.enabled_tools:
                tools.append(
                    types.Tool(
                        name="namma_krushi.agricultural_research_search",
                        description="Search agricultural research, best practices, and scientific literature",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Research query (e.g., 'sustainable farming practices', 'crop rotation benefits')",
                                },
                                "search_type": {
                                    "type": "string",
                                    "enum": ["general", "agricultural", "scientific"],
                                    "description": "Type of search to perform",
                                    "default": "agricultural",
                                },
                            },
                            "required": ["query"],
                        },
                    )
                )

            logger.info(f"Listed {len(tools)} available tools")
            return tools

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any] | None
        ) -> List[types.TextContent]:
            """Handle tool execution requests."""
            try:
                # Sanitize input arguments
                sanitized_args = self.zero_retention_proxy.sanitize_request(
                    arguments or {}
                )

                # Route to appropriate tool handler
                if name == "namma_krushi.disease_analysis":
                    result = await self.disease_tool.analyze(sanitized_args)
                elif name == "namma_krushi.weather_analysis":
                    result = await self.weather_tool.analyze(sanitized_args)
                elif name == "namma_krushi.soil_analysis":
                    result = await self.soil_tool.analyze(sanitized_args)
                elif name == "namma_krushi.government_schemes_search":
                    result = await self.schemes_tool.search(sanitized_args)
                elif name == "namma_krushi.agricultural_research_search":
                    result = await self.research_tool.search(sanitized_args)
                else:
                    raise ValueError(f"Unknown tool: {name}")

                # Sanitize response
                sanitized_result = self.zero_retention_proxy.sanitize_response(result)

                # Create audit log
                self.zero_retention_proxy.create_audit_log(name, sanitized_args, True)

                # Return formatted response
                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(sanitized_result, indent=2, ensure_ascii=False),
                    )
                ]

            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")

                # Create audit log for failure
                self.zero_retention_proxy.create_audit_log(name, sanitized_args, False)

                return [
                    types.TextContent(
                        type="text",
                        text=json.dumps(
                            {
                                "error": "tool_execution_failed",
                                "message": "An error occurred while processing your request. Please try again.",
                                "tool": name,
                            },
                            indent=2,
                        ),
                    )
                ]

    def _setup_resource_handlers(self):
        """Setup resource handlers for agricultural data."""

        @self.server.list_resources()
        async def handle_list_resources() -> List[types.Resource]:
            """List all available agricultural resources."""
            resources = []

            if "crop_calendar" in self.config.enabled_resources:
                resources.append(
                    types.Resource(
                        uri="namma://crop-calendar/karnataka",
                        name="Karnataka Crop Calendar",
                        description="Seasonal crop planting and harvesting calendar for Karnataka",
                        mimeType="application/json",
                    )
                )

            if "disease_database" in self.config.enabled_resources:
                resources.append(
                    types.Resource(
                        uri="namma://disease-database/common",
                        name="Common Crop Diseases Database",
                        description="Database of common crop diseases, symptoms, and treatments",
                        mimeType="application/json",
                    )
                )

            if "weather_patterns" in self.config.enabled_resources:
                resources.append(
                    types.Resource(
                        uri="namma://weather-patterns/karnataka",
                        name="Karnataka Weather Patterns",
                        description="Historical weather patterns and seasonal forecasts for Karnataka",
                        mimeType="application/json",
                    )
                )

            if "soil_types" in self.config.enabled_resources:
                resources.append(
                    types.Resource(
                        uri="namma://soil-types/karnataka",
                        name="Karnataka Soil Types",
                        description="Soil type classifications and properties across Karnataka",
                        mimeType="application/json",
                    )
                )

            logger.info(f"Listed {len(resources)} available resources")
            return resources

        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Handle resource read requests."""
            try:
                if uri == "namma://crop-calendar/karnataka":
                    data = await self.crop_calendar.get_calendar()
                elif uri == "namma://disease-database/common":
                    data = await self.disease_database.get_database()
                elif uri == "namma://weather-patterns/karnataka":
                    data = {"message": "Weather patterns resource not yet implemented"}
                elif uri == "namma://soil-types/karnataka":
                    data = {"message": "Soil types resource not yet implemented"}
                else:
                    raise ValueError(f"Unknown resource URI: {uri}")

                # Sanitize resource data
                sanitized_data = self.zero_retention_proxy.sanitize_response(data)

                return json.dumps(sanitized_data, indent=2, ensure_ascii=False)

            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                return json.dumps(
                    {
                        "error": "resource_read_failed",
                        "message": "Unable to read the requested resource",
                        "uri": uri,
                    },
                    indent=2,
                )

    def _setup_prompt_handlers(self):
        """Setup prompt handlers for agricultural assistance."""

        @self.server.list_prompts()
        async def handle_list_prompts() -> List[types.Prompt]:
            """List all available agricultural prompts."""
            prompts = []

            if "disease_diagnosis" in self.config.enabled_prompts:
                prompts.append(
                    types.Prompt(
                        name="disease_diagnosis",
                        description="Structured prompt for crop disease diagnosis and treatment recommendations",
                        arguments=[
                            types.PromptArgument(
                                name="crop_type",
                                description="Type of crop being analyzed",
                                required=True,
                            ),
                            types.PromptArgument(
                                name="symptoms",
                                description="Observed symptoms and signs",
                                required=True,
                            ),
                            types.PromptArgument(
                                name="location",
                                description="Geographic location",
                                required=False,
                            ),
                        ],
                    )
                )

            if "crop_planning" in self.config.enabled_prompts:
                prompts.append(
                    types.Prompt(
                        name="crop_planning",
                        description="Comprehensive crop planning and management guidance",
                        arguments=[
                            types.PromptArgument(
                                name="crop_type",
                                description="Intended crop to grow",
                                required=True,
                            ),
                            types.PromptArgument(
                                name="season",
                                description="Planting season (Kharif/Rabi/Summer)",
                                required=True,
                            ),
                            types.PromptArgument(
                                name="soil_type",
                                description="Soil type and properties",
                                required=False,
                            ),
                        ],
                    )
                )

            logger.info(f"Listed {len(prompts)} available prompts")
            return prompts

        @self.server.get_prompt()
        async def handle_get_prompt(
            name: str, arguments: Dict[str, str] | None
        ) -> types.GetPromptResult:
            """Handle prompt generation requests."""
            try:
                # Sanitize arguments
                sanitized_args = self.zero_retention_proxy.sanitize_request(
                    arguments or {}
                )

                if name == "disease_diagnosis":
                    prompt_text = await self.prompts.get_disease_diagnosis_prompt(
                        sanitized_args
                    )
                elif name == "crop_planning":
                    prompt_text = await self.prompts.get_crop_planning_prompt(
                        sanitized_args
                    )
                else:
                    raise ValueError(f"Unknown prompt: {name}")

                return types.GetPromptResult(
                    description=f"Generated {name} prompt",
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(type="text", text=prompt_text),
                        )
                    ],
                )

            except Exception as e:
                logger.error(f"Error generating prompt {name}: {e}")
                return types.GetPromptResult(
                    description=f"Error generating {name} prompt",
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=f"Error: Unable to generate prompt. {str(e)}",
                            ),
                        )
                    ],
                )

    async def run(self, transport_type: str = "stdio"):
        """
        Run the MCP server.

        Args:
            transport_type: Transport mechanism ("stdio" or "http")
        """
        logger.info(f"Starting NammaKrushi MCP server with {transport_type} transport")

        if transport_type == "stdio":
            # For local development and testing
            from mcp.server.stdio import stdio_server

            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name=self.config.name,
                        server_version=self.config.version,
                        capabilities=self.server.get_capabilities(
                            notification_options=None, experimental_capabilities={}
                        ),
                    ),
                )
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")


# Global server instance
_mcp_server = None


def get_mcp_server() -> NammaKrushiMCPServer:
    """Get the global MCP server instance."""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = NammaKrushiMCPServer()
    return _mcp_server


async def main():
    """Main entry point for running the MCP server."""
    server = get_mcp_server()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
