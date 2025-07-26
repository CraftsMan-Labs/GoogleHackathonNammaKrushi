"""
Crop Management Tools for Agricultural Assistant

Provides AI tools for creating, updating, and retrieving crop information.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session

from ..config.database import SessionLocal
from ..models.crop import Crop
from ..models.user import User


def get_db_session():
    """Get database session for tools."""
    return SessionLocal()


async def create_crop_tool(
    user_id: int,
    crop_name: str,
    latitude: float,
    longitude: float,
    total_area_acres: float,
    current_crop: str,
    crop_variety: Optional[str] = None,
    planting_date: Optional[str] = None,
    expected_harvest_date: Optional[str] = None,
    soil_type: Optional[str] = None,
    irrigation_type: Optional[str] = None,
    address: Optional[str] = None,
    village: Optional[str] = None,
    district: Optional[str] = None,
    state: str = "Karnataka",
) -> Dict[str, Any]:
    """
    Create a new crop record for a user.

    Args:
        user_id (int): User ID
        crop_name (str): Name/identifier for the crop field
        latitude (float): Latitude coordinate
        longitude (float): Longitude coordinate
        total_area_acres (float): Total area in acres
        current_crop (str): Current crop being grown
        crop_variety (str, optional): Variety of the crop
        planting_date (str, optional): Planting date (YYYY-MM-DD)
        expected_harvest_date (str, optional): Expected harvest date (YYYY-MM-DD)
        soil_type (str, optional): Type of soil
        irrigation_type (str, optional): Irrigation method
        address (str, optional): Address of the field
        village (str, optional): Village name
        district (str, optional): District name
        state (str): State name (default: Karnataka)

    Returns:
        Dict[str, Any]: Result with crop information or error
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

        # Generate unique crop code
        crop_code = f"CROP_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Parse dates if provided
        planting_date_obj = None
        expected_harvest_date_obj = None

        if planting_date:
            try:
                planting_date_obj = datetime.strptime(planting_date, "%Y-%m-%d").date()
            except ValueError:
                return {
                    "status": "error",
                    "error_message": "Invalid planting_date format. Use YYYY-MM-DD",
                }

        if expected_harvest_date:
            try:
                expected_harvest_date_obj = datetime.strptime(
                    expected_harvest_date, "%Y-%m-%d"
                ).date()
            except ValueError:
                return {
                    "status": "error",
                    "error_message": "Invalid expected_harvest_date format. Use YYYY-MM-DD",
                }

        # Create crop record
        crop = Crop(
            user_id=user_id,
            crop_name=crop_name,
            crop_code=crop_code,
            latitude=latitude,
            longitude=longitude,
            total_area_acres=total_area_acres,
            current_crop=current_crop,
            crop_variety=crop_variety,
            planting_date=planting_date_obj,
            expected_harvest_date=expected_harvest_date_obj,
            soil_type=soil_type,
            irrigation_type=irrigation_type,
            address=address,
            village=village,
            district=district,
            state=state,
            crop_stage="seedling",  # Default stage
        )

        db.add(crop)
        db.commit()
        db.refresh(crop)

        logging.info(f"Created crop {crop.id} for user {user_id}")

        return {
            "status": "success",
            "crop_id": crop.id,
            "crop_code": crop.crop_code,
            "crop_name": crop.crop_name,
            "current_crop": crop.current_crop,
            "total_area_acres": crop.total_area_acres,
            "planting_date": crop.planting_date.isoformat()
            if crop.planting_date
            else None,
            "crop_stage": crop.crop_stage,
            "message": f"Successfully created crop '{crop_name}' with {total_area_acres} acres of {current_crop}",
        }

    except Exception as e:
        logging.error(f"Error creating crop: {str(e)}")
        return {"status": "error", "error_message": f"Failed to create crop: {str(e)}"}
    finally:
        db.close()


async def update_crop_tool(
    crop_id: int,
    user_id: int,
    crop_stage: Optional[str] = None,
    crop_health_score: Optional[float] = None,
    current_crop: Optional[str] = None,
    crop_variety: Optional[str] = None,
    planting_date: Optional[str] = None,
    expected_harvest_date: Optional[str] = None,
    total_area_acres: Optional[float] = None,
    cultivable_area_acres: Optional[float] = None,
    soil_type: Optional[str] = None,
    irrigation_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update an existing crop record.

    Args:
        crop_id (int): Crop ID to update
        user_id (int): User ID (for verification)
        crop_stage (str, optional): Current growth stage
        crop_health_score (float, optional): Health score (0-100)
        current_crop (str, optional): Current crop type
        crop_variety (str, optional): Crop variety
        planting_date (str, optional): Planting date (YYYY-MM-DD)
        expected_harvest_date (str, optional): Expected harvest date (YYYY-MM-DD)
        total_area_acres (float, optional): Total area in acres
        cultivable_area_acres (float, optional): Cultivable area in acres
        soil_type (str, optional): Soil type
        irrigation_type (str, optional): Irrigation method

    Returns:
        Dict[str, Any]: Result with updated crop information or error
    """
    db = get_db_session()

    try:
        # Find crop and verify ownership
        crop = (
            db.query(Crop).filter(Crop.id == crop_id, Crop.user_id == user_id).first()
        )

        if not crop:
            return {
                "status": "error",
                "error_message": f"Crop with ID {crop_id} not found or not owned by user {user_id}",
            }

        # Update fields if provided
        updates = {}

        if crop_stage is not None:
            crop.crop_stage = crop_stage
            updates["crop_stage"] = crop_stage

        if crop_health_score is not None:
            if 0 <= crop_health_score <= 100:
                crop.crop_health_score = crop_health_score
                updates["crop_health_score"] = crop_health_score
            else:
                return {
                    "status": "error",
                    "error_message": "crop_health_score must be between 0 and 100",
                }

        if current_crop is not None:
            crop.current_crop = current_crop
            updates["current_crop"] = current_crop

        if crop_variety is not None:
            crop.crop_variety = crop_variety
            updates["crop_variety"] = crop_variety

        if total_area_acres is not None:
            crop.total_area_acres = total_area_acres
            updates["total_area_acres"] = total_area_acres

        if cultivable_area_acres is not None:
            crop.cultivable_area_acres = cultivable_area_acres
            updates["cultivable_area_acres"] = cultivable_area_acres

        if soil_type is not None:
            crop.soil_type = soil_type
            updates["soil_type"] = soil_type

        if irrigation_type is not None:
            crop.irrigation_type = irrigation_type
            updates["irrigation_type"] = irrigation_type

        # Handle date updates
        if planting_date is not None:
            try:
                crop.planting_date = datetime.strptime(planting_date, "%Y-%m-%d").date()
                updates["planting_date"] = planting_date
            except ValueError:
                return {
                    "status": "error",
                    "error_message": "Invalid planting_date format. Use YYYY-MM-DD",
                }

        if expected_harvest_date is not None:
            try:
                crop.expected_harvest_date = datetime.strptime(
                    expected_harvest_date, "%Y-%m-%d"
                ).date()
                updates["expected_harvest_date"] = expected_harvest_date
            except ValueError:
                return {
                    "status": "error",
                    "error_message": "Invalid expected_harvest_date format. Use YYYY-MM-DD",
                }

        db.commit()
        db.refresh(crop)

        logging.info(f"Updated crop {crop_id} for user {user_id}")

        return {
            "status": "success",
            "crop_id": crop.id,
            "crop_name": crop.crop_name,
            "updates_applied": updates,
            "current_stage": crop.crop_stage,
            "health_score": crop.crop_health_score,
            "message": f"Successfully updated crop '{crop.crop_name}'",
        }

    except Exception as e:
        logging.error(f"Error updating crop: {str(e)}")
        return {"status": "error", "error_message": f"Failed to update crop: {str(e)}"}
    finally:
        db.close()


async def get_crops_tool(
    user_id: int,
    crop_id: Optional[int] = None,
    current_crop: Optional[str] = None,
    crop_stage: Optional[str] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Get crop information for a user.

    Args:
        user_id (int): User ID
        crop_id (int, optional): Specific crop ID to retrieve
        current_crop (str, optional): Filter by crop type
        crop_stage (str, optional): Filter by growth stage
        limit (int): Maximum number of crops to return (default: 10)

    Returns:
        Dict[str, Any]: Result with crop information or error
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
        query = db.query(Crop).filter(Crop.user_id == user_id)

        if crop_id is not None:
            query = query.filter(Crop.id == crop_id)

        if current_crop is not None:
            query = query.filter(Crop.current_crop.ilike(f"%{current_crop}%"))

        if crop_stage is not None:
            query = query.filter(Crop.crop_stage == crop_stage)

        # Execute query
        crops = query.order_by(Crop.created_at.desc()).limit(limit).all()

        if not crops:
            return {
                "status": "success",
                "crops": [],
                "total_count": 0,
                "message": "No crops found matching the criteria",
            }

        # Format crop data
        crops_data = []
        for crop in crops:
            crop_info = {
                "crop_id": crop.id,
                "crop_code": crop.crop_code,
                "crop_name": crop.crop_name,
                "current_crop": crop.current_crop,
                "crop_variety": crop.crop_variety,
                "crop_stage": crop.crop_stage,
                "crop_health_score": crop.crop_health_score,
                "total_area_acres": crop.total_area_acres,
                "cultivable_area_acres": crop.cultivable_area_acres,
                "planting_date": crop.planting_date.isoformat()
                if crop.planting_date
                else None,
                "expected_harvest_date": crop.expected_harvest_date.isoformat()
                if crop.expected_harvest_date
                else None,
                "soil_type": crop.soil_type,
                "irrigation_type": crop.irrigation_type,
                "location": {
                    "latitude": crop.latitude,
                    "longitude": crop.longitude,
                    "address": crop.address,
                    "village": crop.village,
                    "district": crop.district,
                    "state": crop.state,
                },
                "created_at": crop.created_at.isoformat(),
                "updated_at": crop.updated_at.isoformat(),
            }
            crops_data.append(crop_info)

        logging.info(f"Retrieved {len(crops)} crops for user {user_id}")

        return {
            "status": "success",
            "crops": crops_data,
            "total_count": len(crops_data),
            "message": f"Found {len(crops_data)} crop(s)",
        }

    except Exception as e:
        logging.error(f"Error retrieving crops: {str(e)}")
        return {
            "status": "error",
            "error_message": f"Failed to retrieve crops: {str(e)}",
        }
    finally:
        db.close()


# Tool declarations for Gemini AI
CREATE_CROP_TOOL_DECLARATION = {
    "name": "create_crop_tool",
    "description": "Create a new crop record for a farmer with location and crop details",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "integer", "description": "User ID of the farmer"},
            "crop_name": {
                "type": "string",
                "description": "Name/identifier for the crop field",
            },
            "latitude": {
                "type": "number",
                "description": "Latitude coordinate of the field",
            },
            "longitude": {
                "type": "number",
                "description": "Longitude coordinate of the field",
            },
            "total_area_acres": {
                "type": "number",
                "description": "Total area in acres",
            },
            "current_crop": {
                "type": "string",
                "description": "Current crop being grown",
            },
            "crop_variety": {"type": "string", "description": "Variety of the crop"},
            "planting_date": {
                "type": "string",
                "description": "Planting date in YYYY-MM-DD format",
            },
            "expected_harvest_date": {
                "type": "string",
                "description": "Expected harvest date in YYYY-MM-DD format",
            },
            "soil_type": {"type": "string", "description": "Type of soil"},
            "irrigation_type": {
                "type": "string",
                "description": "Irrigation method used",
            },
            "address": {"type": "string", "description": "Address of the field"},
            "village": {"type": "string", "description": "Village name"},
            "district": {"type": "string", "description": "District name"},
            "state": {"type": "string", "description": "State name"},
        },
        "required": [
            "user_id",
            "crop_name",
            "latitude",
            "longitude",
            "total_area_acres",
            "current_crop",
        ],
    },
}

UPDATE_CROP_TOOL_DECLARATION = {
    "name": "update_crop_tool",
    "description": "Update an existing crop record with new information",
    "parameters": {
        "type": "object",
        "properties": {
            "crop_id": {"type": "integer", "description": "Crop ID to update"},
            "user_id": {"type": "integer", "description": "User ID for verification"},
            "crop_stage": {
                "type": "string",
                "description": "Current growth stage (seedling, vegetative, flowering, fruiting, harvesting)",
            },
            "crop_health_score": {
                "type": "number",
                "description": "Health score between 0-100",
            },
            "current_crop": {"type": "string", "description": "Current crop type"},
            "crop_variety": {"type": "string", "description": "Crop variety"},
            "planting_date": {
                "type": "string",
                "description": "Planting date in YYYY-MM-DD format",
            },
            "expected_harvest_date": {
                "type": "string",
                "description": "Expected harvest date in YYYY-MM-DD format",
            },
            "total_area_acres": {
                "type": "number",
                "description": "Total area in acres",
            },
            "cultivable_area_acres": {
                "type": "number",
                "description": "Cultivable area in acres",
            },
            "soil_type": {"type": "string", "description": "Soil type"},
            "irrigation_type": {"type": "string", "description": "Irrigation method"},
        },
        "required": ["crop_id", "user_id"],
    },
}

GET_CROPS_TOOL_DECLARATION = {
    "name": "get_crops_tool",
    "description": "Retrieve crop information for a farmer",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "integer", "description": "User ID of the farmer"},
            "crop_id": {
                "type": "integer",
                "description": "Specific crop ID to retrieve",
            },
            "current_crop": {"type": "string", "description": "Filter by crop type"},
            "crop_stage": {"type": "string", "description": "Filter by growth stage"},
            "limit": {
                "type": "integer",
                "description": "Maximum number of crops to return (default: 10)",
            },
        },
        "required": ["user_id"],
    },
}
