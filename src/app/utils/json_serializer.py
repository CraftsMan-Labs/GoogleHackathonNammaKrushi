"""
JSON Serialization Utilities

Utilities for handling JSON serialization of complex objects including datetime objects.
"""

import json
import logging
from datetime import datetime, date
from typing import Any, Dict
from decimal import Decimal
from enum import Enum

logger = logging.getLogger(__name__)


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects and other non-serializable types."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, Enum):
            return obj.value
        elif hasattr(obj, "__dict__"):
            # Handle Pydantic models and other objects with __dict__
            return obj.__dict__
        elif hasattr(obj, "dict") and callable(obj.dict):
            # Handle Pydantic models with dict() method
            return obj.dict()
        return super().default(obj)


def serialize_for_json(data: Any) -> Dict[str, Any]:
    """
    Serialize complex data structures for JSON storage.

    Args:
        data: Data to serialize (can contain datetime objects, Pydantic models, etc.)

    Returns:
        Dict that can be safely serialized to JSON
    """
    try:
        # Convert to JSON string and back to dict to handle all serialization
        json_string = json.dumps(data, cls=DateTimeEncoder, ensure_ascii=False)
        return json.loads(json_string)
    except Exception as e:
        logger.error(f"Failed to serialize data for JSON: {e}")
        # Fallback: try to convert manually
        return _manual_serialize(data)


def _manual_serialize(obj: Any) -> Any:
    """
    Manually serialize objects that can't be handled by the JSON encoder.

    Args:
        obj: Object to serialize

    Returns:
        Serialized object
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, dict):
        return {key: _manual_serialize(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_manual_serialize(item) for item in obj]
    elif hasattr(obj, "dict") and callable(obj.dict):
        # Pydantic model
        return _manual_serialize(obj.dict())
    elif hasattr(obj, "__dict__"):
        # Regular object with __dict__
        return _manual_serialize(obj.__dict__)
    else:
        # Try to convert to string as last resort
        try:
            return str(obj)
        except:
            return None


def safe_json_dumps(data: Any, **kwargs) -> str:
    """
    Safely dump data to JSON string with datetime handling.

    Args:
        data: Data to serialize
        **kwargs: Additional arguments for json.dumps

    Returns:
        JSON string
    """
    try:
        return json.dumps(data, cls=DateTimeEncoder, ensure_ascii=False, **kwargs)
    except Exception as e:
        logger.error(f"Failed to dump JSON: {e}")
        # Fallback with manual serialization
        serialized_data = serialize_for_json(data)
        return json.dumps(serialized_data, ensure_ascii=False, **kwargs)


def safe_json_loads(json_string: str) -> Any:
    """
    Safely load JSON string with error handling.

    Args:
        json_string: JSON string to parse

    Returns:
        Parsed data or None if parsing fails
    """
    try:
        return json.loads(json_string)
    except Exception as e:
        logger.error(f"Failed to load JSON: {e}")
        return None


def clean_report_data(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean report data for database storage by handling datetime serialization.

    Args:
        report_data: Raw report data that may contain datetime objects

    Returns:
        Cleaned report data safe for JSON storage
    """
    try:
        # Use the serialization function to clean the data
        cleaned_data = serialize_for_json(report_data)

        # Additional cleaning for specific known issues
        if isinstance(cleaned_data, dict):
            # Handle timestamp field specifically
            if "timestamp" in cleaned_data and isinstance(
                cleaned_data["timestamp"], datetime
            ):
                cleaned_data["timestamp"] = cleaned_data["timestamp"].isoformat()

            # Recursively clean nested dictionaries
            for key, value in cleaned_data.items():
                if isinstance(value, dict):
                    cleaned_data[key] = clean_report_data(value)
                elif isinstance(value, list):
                    cleaned_data[key] = [
                        clean_report_data(item)
                        if isinstance(item, dict)
                        else _manual_serialize(item)
                        for item in value
                    ]

        return cleaned_data

    except Exception as e:
        logger.error(f"Failed to clean report data: {e}")
        # Return a minimal safe version
        return {
            "error": "Failed to serialize report data",
            "original_keys": list(report_data.keys())
            if isinstance(report_data, dict)
            else [],
            "timestamp": datetime.now().isoformat(),
        }
