"""
Daily Log Management Tools for Agricultural Assistant

Provides AI tools for creating, updating, and retrieving daily farming logs.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session

from ..config.database import SessionLocal
from ..models.daily_log import DailyLog
from ..models.crop import Crop
from ..models.user import User


def get_db_session():
    """Get database session for tools."""
    return SessionLocal()


async def create_daily_log_tool(
    user_id: int,
    crop_id: int,
    log_date: str,
    activity_type: str,
    description: str,
    weather_condition: Optional[str] = None,
    temperature: Optional[float] = None,
    humidity: Optional[float] = None,
    rainfall: Optional[float] = None,
    irrigation_duration: Optional[float] = None,
    fertilizer_applied: Optional[str] = None,
    pesticide_applied: Optional[str] = None,
    labor_hours: Optional[float] = None,
    cost_incurred: Optional[float] = None,
    observations: Optional[str] = None,
    issues_found: Optional[str] = None,
    actions_taken: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new daily log entry for a specific crop.

    Args:
        user_id (int): User ID
        crop_id (int): Crop ID to log for
        log_date (str): Date of the log entry (YYYY-MM-DD)
        activity_type (str): Type of activity (irrigation, fertilization, pest_control, harvesting, etc.)
        description (str): Description of the activity
        weather_condition (str, optional): Weather condition
        temperature (float, optional): Temperature in Celsius
        humidity (float, optional): Humidity percentage
        rainfall (float, optional): Rainfall in mm
        irrigation_duration (float, optional): Irrigation duration in hours
        fertilizer_applied (str, optional): Fertilizer details
        pesticide_applied (str, optional): Pesticide details
        labor_hours (float, optional): Labor hours spent
        cost_incurred (float, optional): Cost incurred
        observations (str, optional): General observations
        issues_found (str, optional): Issues or problems found
        actions_taken (str, optional): Actions taken to address issues

    Returns:
        Dict[str, Any]: Result with log information or error
    """
    db = get_db_session()

    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {
                "status": "error",
                "error_message": f"User with ID {user_id} not found",
            }

        # Verify crop exists and belongs to user
        crop = (
            db.query(Crop).filter(Crop.id == crop_id, Crop.user_id == user_id).first()
        )

        if not crop:
            return {
                "status": "error",
                "error_message": f"Crop with ID {crop_id} not found or not owned by user {user_id}",
            }

        # Parse log date
        try:
            log_date_obj = datetime.strptime(log_date, "%Y-%m-%d").date()
        except ValueError:
            return {
                "status": "error",
                "error_message": "Invalid log_date format. Use YYYY-MM-DD",
            }

        # Create daily log entry
        daily_log = DailyLog(
            user_id=user_id,
            crop_id=crop_id,
            log_date=log_date_obj,
            activity_type=activity_type,
            description=description,
            weather_condition=weather_condition,
            temperature=temperature,
            humidity=humidity,
            rainfall=rainfall,
            irrigation_duration=irrigation_duration,
            fertilizer_applied=fertilizer_applied,
            pesticide_applied=pesticide_applied,
            labor_hours=labor_hours,
            cost_incurred=cost_incurred,
            observations=observations,
            issues_found=issues_found,
            actions_taken=actions_taken,
        )

        db.add(daily_log)
        db.commit()
        db.refresh(daily_log)

        logging.info(
            f"Created daily log {daily_log.id} for crop {crop_id} by user {user_id}"
        )

        return {
            "status": "success",
            "log_id": daily_log.id,
            "crop_id": crop_id,
            "crop_name": crop.crop_name,
            "current_crop": crop.current_crop,
            "log_date": daily_log.log_date.isoformat(),
            "activity_type": daily_log.activity_type,
            "description": daily_log.description,
            "cost_incurred": daily_log.cost_incurred,
            "message": f"Successfully logged {activity_type} activity for {crop.current_crop} on {log_date}",
        }

    except Exception as e:
        logging.error(f"Error creating daily log: {str(e)}")
        return {
            "status": "error",
            "error_message": f"Failed to create daily log: {str(e)}",
        }
    finally:
        db.close()


async def update_daily_log_tool(
    log_id: int,
    user_id: int,
    activity_type: Optional[str] = None,
    description: Optional[str] = None,
    weather_condition: Optional[str] = None,
    temperature: Optional[float] = None,
    humidity: Optional[float] = None,
    rainfall: Optional[float] = None,
    irrigation_duration: Optional[float] = None,
    fertilizer_applied: Optional[str] = None,
    pesticide_applied: Optional[str] = None,
    labor_hours: Optional[float] = None,
    cost_incurred: Optional[float] = None,
    observations: Optional[str] = None,
    issues_found: Optional[str] = None,
    actions_taken: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update an existing daily log entry.

    Args:
        log_id (int): Daily log ID to update
        user_id (int): User ID (for verification)
        activity_type (str, optional): Type of activity
        description (str, optional): Description of the activity
        weather_condition (str, optional): Weather condition
        temperature (float, optional): Temperature in Celsius
        humidity (float, optional): Humidity percentage
        rainfall (float, optional): Rainfall in mm
        irrigation_duration (float, optional): Irrigation duration in hours
        fertilizer_applied (str, optional): Fertilizer details
        pesticide_applied (str, optional): Pesticide details
        labor_hours (float, optional): Labor hours spent
        cost_incurred (float, optional): Cost incurred
        observations (str, optional): General observations
        issues_found (str, optional): Issues or problems found
        actions_taken (str, optional): Actions taken to address issues

    Returns:
        Dict[str, Any]: Result with updated log information or error
    """
    db = get_db_session()

    try:
        # Find daily log and verify ownership
        daily_log = (
            db.query(DailyLog)
            .filter(DailyLog.id == log_id, DailyLog.user_id == user_id)
            .first()
        )

        if not daily_log:
            return {
                "status": "error",
                "error_message": f"Daily log with ID {log_id} not found or not owned by user {user_id}",
            }

        # Get crop information
        crop = db.query(Crop).filter(Crop.id == daily_log.crop_id).first()

        # Update fields if provided
        updates = {}

        if activity_type is not None:
            daily_log.activity_type = activity_type
            updates["activity_type"] = activity_type

        if description is not None:
            daily_log.description = description
            updates["description"] = description

        if weather_condition is not None:
            daily_log.weather_condition = weather_condition
            updates["weather_condition"] = weather_condition

        if temperature is not None:
            daily_log.temperature = temperature
            updates["temperature"] = temperature

        if humidity is not None:
            daily_log.humidity = humidity
            updates["humidity"] = humidity

        if rainfall is not None:
            daily_log.rainfall = rainfall
            updates["rainfall"] = rainfall

        if irrigation_duration is not None:
            daily_log.irrigation_duration = irrigation_duration
            updates["irrigation_duration"] = irrigation_duration

        if fertilizer_applied is not None:
            daily_log.fertilizer_applied = fertilizer_applied
            updates["fertilizer_applied"] = fertilizer_applied

        if pesticide_applied is not None:
            daily_log.pesticide_applied = pesticide_applied
            updates["pesticide_applied"] = pesticide_applied

        if labor_hours is not None:
            daily_log.labor_hours = labor_hours
            updates["labor_hours"] = labor_hours

        if cost_incurred is not None:
            daily_log.cost_incurred = cost_incurred
            updates["cost_incurred"] = cost_incurred

        if observations is not None:
            daily_log.observations = observations
            updates["observations"] = observations

        if issues_found is not None:
            daily_log.issues_found = issues_found
            updates["issues_found"] = issues_found

        if actions_taken is not None:
            daily_log.actions_taken = actions_taken
            updates["actions_taken"] = actions_taken

        db.commit()
        db.refresh(daily_log)

        logging.info(f"Updated daily log {log_id} for user {user_id}")

        return {
            "status": "success",
            "log_id": daily_log.id,
            "crop_name": crop.crop_name if crop else "Unknown",
            "log_date": daily_log.log_date.isoformat(),
            "updates_applied": updates,
            "activity_type": daily_log.activity_type,
            "message": f"Successfully updated daily log for {daily_log.log_date}",
        }

    except Exception as e:
        logging.error(f"Error updating daily log: {str(e)}")
        return {
            "status": "error",
            "error_message": f"Failed to update daily log: {str(e)}",
        }
    finally:
        db.close()


async def get_daily_logs_tool(
    user_id: int,
    crop_id: Optional[int] = None,
    log_id: Optional[int] = None,
    activity_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """
    Get daily log entries for a user.

    Args:
        user_id (int): User ID
        crop_id (int, optional): Filter by specific crop ID
        log_id (int, optional): Specific log ID to retrieve
        activity_type (str, optional): Filter by activity type
        start_date (str, optional): Start date filter (YYYY-MM-DD)
        end_date (str, optional): End date filter (YYYY-MM-DD)
        limit (int): Maximum number of logs to return (default: 20)

    Returns:
        Dict[str, Any]: Result with log information or error
    """
    db = get_db_session()

    try:
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {
                "status": "error",
                "error_message": f"User with ID {user_id} not found",
            }

        # Build query
        query = db.query(DailyLog).filter(DailyLog.user_id == user_id)

        if log_id is not None:
            query = query.filter(DailyLog.id == log_id)

        if crop_id is not None:
            query = query.filter(DailyLog.crop_id == crop_id)

        if activity_type is not None:
            query = query.filter(DailyLog.activity_type.ilike(f"%{activity_type}%"))

        # Date filters
        if start_date is not None:
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                query = query.filter(DailyLog.log_date >= start_date_obj)
            except ValueError:
                return {
                    "status": "error",
                    "error_message": "Invalid start_date format. Use YYYY-MM-DD",
                }

        if end_date is not None:
            try:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                query = query.filter(DailyLog.log_date <= end_date_obj)
            except ValueError:
                return {
                    "status": "error",
                    "error_message": "Invalid end_date format. Use YYYY-MM-DD",
                }

        # Execute query with crop information
        logs = query.order_by(DailyLog.log_date.desc()).limit(limit).all()

        if not logs:
            return {
                "status": "success",
                "logs": [],
                "total_count": 0,
                "message": "No daily logs found matching the criteria",
            }

        # Format log data with crop information
        logs_data = []
        for log in logs:
            # Get crop information
            crop = db.query(Crop).filter(Crop.id == log.crop_id).first()

            log_info = {
                "log_id": log.id,
                "crop_id": log.crop_id,
                "crop_info": {
                    "crop_name": crop.crop_name if crop else "Unknown",
                    "current_crop": crop.current_crop if crop else "Unknown",
                    "crop_variety": crop.crop_variety if crop else None,
                    "crop_stage": crop.crop_stage if crop else None,
                },
                "log_date": log.log_date.isoformat(),
                "activity_type": log.activity_type,
                "description": log.description,
                "weather": {
                    "condition": log.weather_condition,
                    "temperature": log.temperature,
                    "humidity": log.humidity,
                    "rainfall": log.rainfall,
                },
                "farming_activities": {
                    "irrigation_duration": log.irrigation_duration,
                    "fertilizer_applied": log.fertilizer_applied,
                    "pesticide_applied": log.pesticide_applied,
                    "labor_hours": log.labor_hours,
                    "cost_incurred": log.cost_incurred,
                },
                "observations": log.observations,
                "issues_found": log.issues_found,
                "actions_taken": log.actions_taken,
                "created_at": log.created_at.isoformat(),
                "updated_at": log.updated_at.isoformat(),
            }
            logs_data.append(log_info)

        logging.info(f"Retrieved {len(logs)} daily logs for user {user_id}")

        return {
            "status": "success",
            "logs": logs_data,
            "total_count": len(logs_data),
            "message": f"Found {len(logs_data)} daily log(s)",
        }

    except Exception as e:
        logging.error(f"Error retrieving daily logs: {str(e)}")
        return {
            "status": "error",
            "error_message": f"Failed to retrieve daily logs: {str(e)}",
        }
    finally:
        db.close()


# Tool declarations for Gemini AI
CREATE_DAILY_LOG_TOOL_DECLARATION = {
    "name": "create_daily_log_tool",
    "description": "Create a new daily farming log entry for a specific crop",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "integer", "description": "User ID of the farmer"},
            "crop_id": {"type": "integer", "description": "Crop ID to log for"},
            "log_date": {
                "type": "string",
                "description": "Date of the log entry in YYYY-MM-DD format",
            },
            "activity_type": {
                "type": "string",
                "description": "Type of activity (irrigation, fertilization, pest_control, harvesting, planting, weeding, etc.)",
            },
            "description": {
                "type": "string",
                "description": "Description of the activity performed",
            },
            "weather_condition": {
                "type": "string",
                "description": "Weather condition (sunny, cloudy, rainy, etc.)",
            },
            "temperature": {"type": "number", "description": "Temperature in Celsius"},
            "humidity": {"type": "number", "description": "Humidity percentage"},
            "rainfall": {"type": "number", "description": "Rainfall in mm"},
            "irrigation_duration": {
                "type": "number",
                "description": "Irrigation duration in hours",
            },
            "fertilizer_applied": {
                "type": "string",
                "description": "Details of fertilizer applied",
            },
            "pesticide_applied": {
                "type": "string",
                "description": "Details of pesticide applied",
            },
            "labor_hours": {"type": "number", "description": "Labor hours spent"},
            "cost_incurred": {
                "type": "number",
                "description": "Cost incurred for the activity",
            },
            "observations": {
                "type": "string",
                "description": "General observations about the crop",
            },
            "issues_found": {
                "type": "string",
                "description": "Issues or problems found",
            },
            "actions_taken": {
                "type": "string",
                "description": "Actions taken to address issues",
            },
        },
        "required": ["user_id", "crop_id", "log_date", "activity_type", "description"],
    },
}

UPDATE_DAILY_LOG_TOOL_DECLARATION = {
    "name": "update_daily_log_tool",
    "description": "Update an existing daily farming log entry",
    "parameters": {
        "type": "object",
        "properties": {
            "log_id": {"type": "integer", "description": "Daily log ID to update"},
            "user_id": {"type": "integer", "description": "User ID for verification"},
            "activity_type": {"type": "string", "description": "Type of activity"},
            "description": {
                "type": "string",
                "description": "Description of the activity",
            },
            "weather_condition": {"type": "string", "description": "Weather condition"},
            "temperature": {"type": "number", "description": "Temperature in Celsius"},
            "humidity": {"type": "number", "description": "Humidity percentage"},
            "rainfall": {"type": "number", "description": "Rainfall in mm"},
            "irrigation_duration": {
                "type": "number",
                "description": "Irrigation duration in hours",
            },
            "fertilizer_applied": {
                "type": "string",
                "description": "Fertilizer details",
            },
            "pesticide_applied": {"type": "string", "description": "Pesticide details"},
            "labor_hours": {"type": "number", "description": "Labor hours spent"},
            "cost_incurred": {"type": "number", "description": "Cost incurred"},
            "observations": {"type": "string", "description": "General observations"},
            "issues_found": {"type": "string", "description": "Issues found"},
            "actions_taken": {"type": "string", "description": "Actions taken"},
        },
        "required": ["log_id", "user_id"],
    },
}

GET_DAILY_LOGS_TOOL_DECLARATION = {
    "name": "get_daily_logs_tool",
    "description": "Retrieve daily farming log entries for a farmer, with crop information included",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "integer", "description": "User ID of the farmer"},
            "crop_id": {"type": "integer", "description": "Filter by specific crop ID"},
            "log_id": {"type": "integer", "description": "Specific log ID to retrieve"},
            "activity_type": {
                "type": "string",
                "description": "Filter by activity type",
            },
            "start_date": {
                "type": "string",
                "description": "Start date filter in YYYY-MM-DD format",
            },
            "end_date": {
                "type": "string",
                "description": "End date filter in YYYY-MM-DD format",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of logs to return (default: 20)",
            },
        },
        "required": ["user_id"],
    },
}
