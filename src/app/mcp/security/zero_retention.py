"""
Zero Data Retention Proxy Layer

Ensures no personal or sensitive data is stored by the MCP server.
All requests and responses are sanitized to protect farmer privacy.
"""

import re
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from ..config.mcp_settings import get_zero_retention_config

logger = logging.getLogger(__name__)


class ZeroRetentionProxy:
    """
    Proxy layer that ensures zero data retention while maintaining functionality.

    This class sanitizes all incoming requests and outgoing responses to remove
    personally identifiable information (PII) and sensitive data.
    """

    def __init__(self):
        self.config = get_zero_retention_config()
        self._setup_sanitization_patterns()

    def _setup_sanitization_patterns(self):
        """Setup regex patterns for data sanitization."""
        # Phone number patterns (Indian format)
        self.phone_patterns = [
            r"\+91[0-9]{10}",
            r"91[0-9]{10}",
            r"[0-9]{10}",
            r"\+91\s[0-9]{5}\s[0-9]{5}",
        ]

        # Email patterns
        self.email_patterns = [r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"]

        # ID patterns (database IDs, user IDs)
        self.id_patterns = [
            r"\b(user_id|farmer_id|id|database_id):\s*[0-9]+",
            r'"(user_id|farmer_id|id|database_id)":\s*[0-9]+',
        ]

    def sanitize_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize incoming request data to remove PII and sensitive information.

        Args:
            request_data: Raw request data from MCP client

        Returns:
            Sanitized request data safe for processing
        """
        try:
            sanitized = self._deep_sanitize_dict(request_data.copy())

            # Log sanitization event (without sensitive data)
            self._log_sanitization_event("request", request_data, sanitized)

            return sanitized

        except Exception as e:
            logger.error(f"Error sanitizing request: {e}")
            # Return minimal safe data if sanitization fails
            return {"error": "sanitization_failed"}

    def sanitize_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize outgoing response data to remove sensitive information.

        Args:
            response_data: Raw response data from internal services

        Returns:
            Sanitized response data safe for external consumption
        """
        try:
            sanitized = self._deep_sanitize_dict(response_data.copy())

            # Remove internal system fields
            sanitized = self._remove_internal_fields(sanitized)

            # Log sanitization event (without sensitive data)
            self._log_sanitization_event("response", response_data, sanitized)

            return sanitized

        except Exception as e:
            logger.error(f"Error sanitizing response: {e}")
            # Return error response if sanitization fails
            return {"error": "response_sanitization_failed"}

    def _deep_sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize dictionary data."""
        if not isinstance(data, dict):
            return data

        sanitized = {}

        for key, value in data.items():
            # Skip PII fields entirely
            if key.lower() in [field.lower() for field in self.config.pii_fields]:
                continue

            # Recursively sanitize nested dictionaries
            if isinstance(value, dict):
                sanitized[key] = self._deep_sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = self._sanitize_list(value)
            elif isinstance(value, str):
                sanitized[key] = self._sanitize_string(value)
            else:
                sanitized[key] = value

        return sanitized

    def _sanitize_list(self, data: List[Any]) -> List[Any]:
        """Sanitize list data."""
        sanitized = []
        for item in data:
            if isinstance(item, dict):
                sanitized.append(self._deep_sanitize_dict(item))
            elif isinstance(item, str):
                sanitized.append(self._sanitize_string(item))
            else:
                sanitized.append(item)
        return sanitized

    def _sanitize_string(self, text: str) -> str:
        """Sanitize string data to remove PII patterns."""
        if not isinstance(text, str):
            return text

        sanitized = text

        # Remove phone numbers
        for pattern in self.phone_patterns:
            sanitized = re.sub(pattern, "[PHONE_REDACTED]", sanitized)

        # Remove email addresses
        for pattern in self.email_patterns:
            sanitized = re.sub(pattern, "[EMAIL_REDACTED]", sanitized)

        # Remove ID patterns
        for pattern in self.id_patterns:
            sanitized = re.sub(pattern, "[ID_REDACTED]", sanitized)

        return sanitized

    def _remove_internal_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove internal system fields from response data."""
        if not isinstance(data, dict):
            return data

        # Fields to remove from responses
        fields_to_remove = self.config.sensitive_response_fields

        cleaned = {}
        for key, value in data.items():
            if key not in fields_to_remove:
                if isinstance(value, dict):
                    cleaned[key] = self._remove_internal_fields(value)
                elif isinstance(value, list):
                    cleaned[key] = [
                        self._remove_internal_fields(item)
                        if isinstance(item, dict)
                        else item
                        for item in value
                    ]
                else:
                    cleaned[key] = value

        return cleaned

    def sanitize_location(self, location: str) -> str:
        """
        Sanitize location data to specified precision level.

        Args:
            location: Full location string

        Returns:
            Sanitized location at configured precision level
        """
        if not location:
            return location

        # Split location into components
        parts = [part.strip() for part in location.split(",")]

        if self.config.location_precision == "city" and len(parts) >= 1:
            return parts[0]  # Return only city
        elif self.config.location_precision == "district" and len(parts) >= 2:
            return f"{parts[0]}, {parts[1]}"  # Return city, district
        elif self.config.location_precision == "state" and len(parts) >= 3:
            return f"{parts[0]}, {parts[1]}, {parts[2]}"  # Return city, district, state

        return parts[0] if parts else location

    def _log_sanitization_event(
        self,
        event_type: str,
        original_data: Dict[str, Any],
        sanitized_data: Dict[str, Any],
    ):
        """Log sanitization events for audit purposes (without sensitive data)."""
        try:
            # Create audit log entry with only allowed fields
            audit_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": f"sanitization_{event_type}",
                "fields_removed": len(original_data) - len(sanitized_data),
                "success": True,
            }

            # Add allowed fields if present
            for field in self.config.audit_log_fields:
                if field in sanitized_data:
                    audit_entry[field] = sanitized_data[field]

            logger.info(f"Sanitization audit: {json.dumps(audit_entry)}")

        except Exception as e:
            logger.error(f"Error logging sanitization event: {e}")

    def create_audit_log(
        self, tool_name: str, request_data: Dict[str, Any], success: bool = True
    ):
        """
        Create audit log entry for tool usage (privacy-compliant).

        Args:
            tool_name: Name of the MCP tool used
            request_data: Sanitized request data
            success: Whether the operation was successful
        """
        try:
            audit_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tool_name": tool_name,
                "success": success,
            }

            # Add only allowed audit fields
            for field in self.config.audit_log_fields:
                if field in request_data:
                    if field == "location_city":
                        # Sanitize location to city level
                        location = request_data.get("location", "")
                        audit_entry[field] = self.sanitize_location(location)
                    else:
                        audit_entry[field] = request_data[field]

            logger.info(f"Tool usage audit: {json.dumps(audit_entry)}")

        except Exception as e:
            logger.error(f"Error creating audit log: {e}")


# Global proxy instance
_zero_retention_proxy = ZeroRetentionProxy()


def get_zero_retention_proxy() -> ZeroRetentionProxy:
    """Get the global zero retention proxy instance."""
    return _zero_retention_proxy
