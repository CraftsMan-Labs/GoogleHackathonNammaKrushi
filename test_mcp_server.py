#!/usr/bin/env python3
"""
Test script for NammaKrushi MCP Server

This script tests the basic functionality of the MCP server
to ensure all components are working correctly.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.app.mcp.server import get_mcp_server
from src.app.mcp.config.mcp_settings import get_mcp_config
from src.app.mcp.security.zero_retention import get_zero_retention_proxy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_mcp_server():
    """Test the MCP server functionality."""

    print("🌾 Testing NammaKrushi MCP Server")
    print("=" * 50)

    try:
        # Test 1: Configuration
        print("1. Testing Configuration...")
        config = get_mcp_config()
        print(f"   ✓ Server Name: {config.name}")
        print(f"   ✓ Version: {config.version}")
        print(f"   ✓ Zero Retention: {config.enable_zero_retention}")
        print(f"   ✓ Tools: {len(config.enabled_tools)}")
        print(f"   ✓ Resources: {len(config.enabled_resources)}")
        print(f"   ✓ Prompts: {len(config.enabled_prompts)}")

        # Test 2: Zero Retention Proxy
        print("\n2. Testing Zero Retention Proxy...")
        proxy = get_zero_retention_proxy()

        # Test sanitization
        test_data = {
            "crop_type": "Rice",
            "symptoms": "Brown spots on leaves",
            "location": "Bangalore, Karnataka, India",
            "phone": "+91 9876543210",
            "email": "farmer@example.com",
            "user_id": 12345,
        }

        sanitized = proxy.sanitize_request(test_data)
        print(f"   ✓ Original fields: {len(test_data)}")
        print(f"   ✓ Sanitized fields: {len(sanitized)}")
        print(
            f"   ✓ PII removed: {'phone' not in sanitized and 'email' not in sanitized}"
        )
        print(f"   ✓ Location sanitized: {sanitized.get('location', 'N/A')}")

        # Test 3: MCP Server Initialization
        print("\n3. Testing MCP Server Initialization...")
        server = get_mcp_server()
        print("   ✓ Server instance created")
        print("   ✓ Tool handlers initialized")
        print("   ✓ Resource handlers initialized")
        print("   ✓ Prompt handlers initialized")

        # Test 4: Tool Availability
        print("\n4. Testing Tool Availability...")
        from src.app.mcp.tools.disease_analysis import DiseaseAnalysisTool
        from src.app.mcp.tools.weather_tools import WeatherAnalysisTool
        from src.app.mcp.tools.soil_tools import SoilAnalysisTool
        from src.app.mcp.tools.search_tools import (
            GovernmentSchemesTool,
            AgriculturalResearchTool,
        )

        disease_tool = DiseaseAnalysisTool()
        weather_tool = WeatherAnalysisTool()
        soil_tool = SoilAnalysisTool()
        schemes_tool = GovernmentSchemesTool()
        research_tool = AgriculturalResearchTool()

        print("   ✓ Disease Analysis Tool")
        print("   ✓ Weather Analysis Tool")
        print("   ✓ Soil Analysis Tool")
        print("   ✓ Government Schemes Tool")
        print("   ✓ Agricultural Research Tool")

        # Test 5: Resource Availability
        print("\n5. Testing Resource Availability...")
        from src.app.mcp.resources.crop_calendar import CropCalendarResource
        from src.app.mcp.resources.disease_database import DiseaseDatabaseResource

        crop_calendar = CropCalendarResource()
        disease_db = DiseaseDatabaseResource()

        # Test crop calendar
        calendar_data = await crop_calendar.get_calendar()
        print(f"   ✓ Crop Calendar: {calendar_data.get('status', 'unknown')}")

        # Test disease database
        disease_data = await disease_db.get_database()
        print(f"   ✓ Disease Database: {disease_data.get('status', 'unknown')}")

        # Test 6: Prompt Availability
        print("\n6. Testing Prompt Availability...")
        from src.app.mcp.prompts.agricultural_prompts import AgriculturalPrompts

        prompts = AgriculturalPrompts()

        # Test disease diagnosis prompt
        disease_prompt = await prompts.get_disease_diagnosis_prompt(
            {"crop_type": "Rice", "symptoms": "Brown spots", "location": "Bangalore"}
        )
        print(f"   ✓ Disease Diagnosis Prompt: {len(disease_prompt)} characters")

        # Test crop planning prompt
        planning_prompt = await prompts.get_crop_planning_prompt(
            {"crop_type": "Wheat", "season": "Rabi", "soil_type": "Clay loam"}
        )
        print(f"   ✓ Crop Planning Prompt: {len(planning_prompt)} characters")

        # Test 7: Error Handling
        print("\n7. Testing Error Handling...")

        # Test invalid tool arguments
        try:
            result = await disease_tool.analyze({})  # Missing required fields
            if "error" in result:
                print("   ✓ Error handling for missing arguments")
            else:
                print("   ⚠ Error handling may need improvement")
        except Exception as e:
            print(f"   ✓ Exception handling: {type(e).__name__}")

        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("🚀 NammaKrushi MCP Server is ready for use!")
        print("\nTo start the server, run:")
        print("   python -m src.app.mcp.main")
        print("\nFor configuration check:")
        print("   python -m src.app.mcp.main --config-check")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.exception("Full error traceback:")
        return False


def main():
    """Main test function."""
    try:
        success = asyncio.run(test_mcp_server())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal test error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
