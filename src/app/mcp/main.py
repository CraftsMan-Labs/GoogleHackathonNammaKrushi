"""
NammaKrushi MCP Server Main Entry Point

Main entry point for running the NammaKrushi Model Context Protocol server.
Provides agricultural AI services through standardized MCP interface.
"""

import asyncio
import logging
import sys
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.app.mcp.server import get_mcp_server
from src.app.mcp.config.mcp_settings import get_mcp_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("namma_krushi_mcp.log"),
    ],
)

logger = logging.getLogger(__name__)


def setup_argument_parser() -> argparse.ArgumentParser:
    """Setup command line argument parser."""
    parser = argparse.ArgumentParser(
        description="NammaKrushi MCP Server - Agricultural AI services via Model Context Protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.app.mcp.main                    # Run with stdio transport
  python -m src.app.mcp.main --transport stdio  # Run with stdio transport
  python -m src.app.mcp.main --debug           # Run with debug logging
  
For more information, visit: https://github.com/your-org/namma-krushi
        """,
    )

    parser.add_argument(
        "--transport",
        choices=["stdio"],
        default="stdio",
        help="Transport mechanism for MCP communication (default: stdio)",
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    parser.add_argument(
        "--config-check", action="store_true", help="Check configuration and exit"
    )

    parser.add_argument(
        "--version", action="version", version="NammaKrushi MCP Server 1.0.0"
    )

    return parser


def check_configuration():
    """Check MCP server configuration and dependencies."""
    logger.info("Checking NammaKrushi MCP Server configuration...")

    try:
        # Check MCP configuration
        config = get_mcp_config()
        logger.info(f"✓ MCP Server Name: {config.name}")
        logger.info(f"✓ MCP Server Version: {config.version}")
        logger.info(f"✓ Enabled Tools: {len(config.enabled_tools)}")
        logger.info(f"✓ Enabled Resources: {len(config.enabled_resources)}")
        logger.info(f"✓ Enabled Prompts: {len(config.enabled_prompts)}")
        logger.info(f"✓ Zero Retention: {config.enable_zero_retention}")

        # Check tool availability
        from src.app.mcp.tools.disease_analysis import DiseaseAnalysisTool
        from src.app.mcp.tools.weather_tools import WeatherAnalysisTool
        from src.app.mcp.tools.soil_tools import SoilAnalysisTool
        from src.app.mcp.tools.search_tools import (
            GovernmentSchemesTool,
            AgriculturalResearchTool,
        )

        logger.info("✓ Disease Analysis Tool: Available")
        logger.info("✓ Weather Analysis Tool: Available")
        logger.info("✓ Soil Analysis Tool: Available")
        logger.info("✓ Government Schemes Tool: Available")
        logger.info("✓ Agricultural Research Tool: Available")

        # Check resource availability
        from src.app.mcp.resources.crop_calendar import CropCalendarResource
        from src.app.mcp.resources.disease_database import DiseaseDatabaseResource

        logger.info("✓ Crop Calendar Resource: Available")
        logger.info("✓ Disease Database Resource: Available")

        # Check prompt availability
        from src.app.mcp.prompts.agricultural_prompts import AgriculturalPrompts

        logger.info("✓ Agricultural Prompts: Available")

        # Check zero retention proxy
        from src.app.mcp.security.zero_retention import get_zero_retention_proxy

        proxy = get_zero_retention_proxy()
        logger.info("✓ Zero Retention Proxy: Available")

        logger.info("✅ Configuration check completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Configuration check failed: {e}")
        return False


async def main():
    """Main entry point for the MCP server."""
    parser = setup_argument_parser()
    args = parser.parse_args()

    # Setup debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    # Configuration check
    if args.config_check:
        success = check_configuration()
        sys.exit(0 if success else 1)

    # Display startup banner
    logger.info("=" * 60)
    logger.info("🌾 NammaKrushi MCP Server Starting")
    logger.info("   AI-Powered Agricultural Assistant")
    logger.info("   Model Context Protocol Interface")
    logger.info("=" * 60)

    try:
        # Check configuration before starting
        if not check_configuration():
            logger.error("Configuration check failed. Exiting.")
            sys.exit(1)

        # Initialize and start MCP server
        logger.info(f"Starting MCP server with {args.transport} transport...")

        server = get_mcp_server()

        # Display server information
        config = get_mcp_config()
        logger.info(f"Server Name: {config.name}")
        logger.info(f"Server Version: {config.version}")
        logger.info(
            f"Zero Data Retention: {'Enabled' if config.enable_zero_retention else 'Disabled'}"
        )
        logger.info(f"Available Tools: {len(config.enabled_tools)}")
        logger.info(f"Available Resources: {len(config.enabled_resources)}")
        logger.info(f"Available Prompts: {len(config.enabled_prompts)}")

        logger.info("🚀 MCP Server ready for connections!")
        logger.info("Connect your MCP client to start using NammaKrushi services.")

        # Run the server
        await server.run(transport_type=args.transport)

    except KeyboardInterrupt:
        logger.info("🛑 Server shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        if args.debug:
            logger.exception("Full error traceback:")
        sys.exit(1)
    finally:
        logger.info("👋 NammaKrushi MCP Server stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Server interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
