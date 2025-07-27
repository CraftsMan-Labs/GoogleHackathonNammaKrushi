"""
MCP Server Configuration Settings

Configuration for the NammaKrushi Model Context Protocol server.
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from ..config.settings import settings


class MCPServerConfig(BaseModel):
    """Configuration for MCP server."""

    # Server identification
    name: str = "namma-krushi"
    version: str = "1.0.0"
    description: str = "AI-powered agricultural assistant for Karnataka farmers"

    # Server capabilities
    supports_tools: bool = True
    supports_resources: bool = True
    supports_prompts: bool = True
    supports_sampling: bool = False  # We don't need LLM sampling

    # Zero retention settings
    enable_zero_retention: bool = True
    log_requests: bool = True  # Log patterns, not data
    sanitize_responses: bool = True

    # Rate limiting
    max_requests_per_minute: int = 100
    max_concurrent_requests: int = 10

    # Tool configuration
    enabled_tools: List[str] = Field(
        default_factory=lambda: [
            "disease_analysis",
            "weather_analysis",
            "soil_analysis",
            "government_schemes_search",
            "agricultural_research_search",
            "crop_management_read",
        ]
    )

    # Resource configuration
    enabled_resources: List[str] = Field(
        default_factory=lambda: [
            "crop_calendar",
            "disease_database",
            "weather_patterns",
            "soil_types",
        ]
    )

    # Prompt configuration
    enabled_prompts: List[str] = Field(
        default_factory=lambda: [
            "disease_diagnosis",
            "crop_planning",
            "weather_advisory",
            "soil_analysis",
        ]
    )


class ZeroRetentionConfig(BaseModel):
    """Configuration for zero data retention."""

    # PII fields to remove from requests
    pii_fields: List[str] = Field(
        default_factory=lambda: [
            "phone",
            "email",
            "name",
            "address",
            "user_id",
            "farmer_id",
            "contact",
            "personal_id",
        ]
    )

    # Sensitive fields to remove from responses
    sensitive_response_fields: List[str] = Field(
        default_factory=lambda: [
            "id",
            "user_id",
            "farmer_id",
            "database_id",
            "internal_id",
            "session_id",
            "auth_token",
        ]
    )

    # Location precision (city level only)
    location_precision: str = "city"  # city, district, state

    # Data retention period for audit logs (in days)
    audit_log_retention_days: int = 30

    # Fields allowed in audit logs
    audit_log_fields: List[str] = Field(
        default_factory=lambda: [
            "tool_name",
            "timestamp",
            "location_city",
            "crop_type",
            "request_type",
            "success",
        ]
    )


# Global configuration instances
mcp_config = MCPServerConfig()
zero_retention_config = ZeroRetentionConfig()


def get_mcp_config() -> MCPServerConfig:
    """Get MCP server configuration."""
    return mcp_config


def get_zero_retention_config() -> ZeroRetentionConfig:
    """Get zero retention configuration."""
    return zero_retention_config
