"""
Sales Management Tools for Agricultural Assistant

Provides AI tools for creating, updating, and retrieving sales information.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session

from ..config.database import SessionLocal
from ..models.sale import Sale
from ..models.crop import Crop
from ..models.user import User


def get_db_session():
    """Get database session for tools."""
    return SessionLocal()


async def create_sale_tool(
    user_id: int,
    crop_id: int,
    sale_date: Optional[str] = None,
    crop_type: Optional[str] = None,
    crop_variety: Optional[str] = None,
    quantity_kg: Optional[float] = None,
    price_per_kg: Optional[float] = None,
    total_amount: Optional[float] = None,
    buyer_name: Optional[str] = None,
    buyer_type: Optional[str] = None,
    buyer_contact: Optional[str] = None,
    payment_method: Optional[str] = None,
    payment_status: str = "pending",
    transportation_cost: Optional[float] = None,
    commission_paid: Optional[float] = None,
    quality_grade: Optional[str] = None,
    quality_notes: Optional[str] = None,
    market_location: Optional[str] = None,
    market_price_reference: Optional[float] = None,
    notes: Optional[str] = None,
    invoice_number: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new sale record for a crop.

    Args:
        user_id (int): User ID (for verification)
        crop_id (int): Crop ID for the sale
        sale_date (str, optional): Sale date (YYYY-MM-DD, defaults to today)
        crop_type (str, optional): Type of crop sold
        crop_variety (str, optional): Variety of crop sold
        quantity_kg (float, optional): Quantity sold in kg
        price_per_kg (float, optional): Price per kg
        total_amount (float, optional): Total sale amount
        buyer_name (str, optional): Name of buyer
        buyer_type (str, optional): Type of buyer (direct, market, middleman, export, online)
        buyer_contact (str, optional): Buyer contact information
        payment_method (str, optional): Payment method (cash, bank_transfer, cheque, upi)
        payment_status (str): Payment status (pending, completed, partial)
        transportation_cost (float, optional): Transportation cost
        commission_paid (float, optional): Commission paid
        quality_grade (str, optional): Quality grade (A, B, C)
        quality_notes (str, optional): Quality notes
        market_location (str, optional): Market location
        market_price_reference (float, optional): Reference market price
        notes (str, optional): Additional notes
        invoice_number (str, optional): Invoice number

    Returns:
        Dict[str, Any]: Result with sale information or error
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

        # Parse sale date if provided
        sale_date_obj = date.today()
        if sale_date:
            try:
                sale_date_obj = datetime.strptime(sale_date, "%Y-%m-%d").date()
            except ValueError:
                return {
                    "status": "error",
                    "error_message": "Invalid sale_date format. Use YYYY-MM-DD",
                }

        # Auto-calculate total amount if not provided
        if (
            total_amount is None
            and quantity_kg is not None
            and price_per_kg is not None
        ):
            total_amount = quantity_kg * price_per_kg

        # Create sale record
        sale = Sale(
            crop_id=crop_id,
            sale_date=sale_date_obj,
            crop_type=crop_type or crop.current_crop,
            crop_variety=crop_variety or crop.crop_variety,
            quantity_kg=quantity_kg,
            price_per_kg=price_per_kg,
            total_amount=total_amount,
            buyer_name=buyer_name,
            buyer_type=buyer_type,
            buyer_contact=buyer_contact,
            payment_method=payment_method,
            payment_status=payment_status,
            transportation_cost=transportation_cost,
            commission_paid=commission_paid,
            quality_grade=quality_grade,
            quality_notes=quality_notes,
            market_location=market_location,
            market_price_reference=market_price_reference,
            notes=notes,
            invoice_number=invoice_number,
        )

        db.add(sale)
        db.commit()
        db.refresh(sale)

        logging.info(f"Created sale {sale.id} for crop {crop_id}")

        return {
            "status": "success",
            "sale_id": sale.id,
            "crop_id": sale.crop_id,
            "sale_date": sale.sale_date.isoformat(),
            "crop_type": sale.crop_type,
            "quantity_kg": sale.quantity_kg,
            "price_per_kg": sale.price_per_kg,
            "total_amount": sale.total_amount,
            "buyer_name": sale.buyer_name,
            "payment_status": sale.payment_status,
            "message": f"Successfully created sale record for {sale.quantity_kg}kg of {sale.crop_type} at ₹{sale.price_per_kg}/kg",
        }

    except Exception as e:
        logging.error(f"Error creating sale: {str(e)}")
        return {"status": "error", "error_message": f"Failed to create sale: {str(e)}"}
    finally:
        db.close()


async def update_sale_tool(
    sale_id: int,
    user_id: int,
    crop_type: Optional[str] = None,
    crop_variety: Optional[str] = None,
    quantity_kg: Optional[float] = None,
    price_per_kg: Optional[float] = None,
    total_amount: Optional[float] = None,
    buyer_name: Optional[str] = None,
    buyer_type: Optional[str] = None,
    buyer_contact: Optional[str] = None,
    payment_method: Optional[str] = None,
    payment_status: Optional[str] = None,
    transportation_cost: Optional[float] = None,
    commission_paid: Optional[float] = None,
    quality_grade: Optional[str] = None,
    quality_notes: Optional[str] = None,
    market_location: Optional[str] = None,
    market_price_reference: Optional[float] = None,
    notes: Optional[str] = None,
    invoice_number: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update an existing sale record.

    Args:
        sale_id (int): Sale ID to update
        user_id (int): User ID (for verification)
        crop_type (str, optional): Type of crop sold
        crop_variety (str, optional): Variety of crop sold
        quantity_kg (float, optional): Quantity sold in kg
        price_per_kg (float, optional): Price per kg
        total_amount (float, optional): Total sale amount
        buyer_name (str, optional): Name of buyer
        buyer_type (str, optional): Type of buyer
        buyer_contact (str, optional): Buyer contact information
        payment_method (str, optional): Payment method
        payment_status (str, optional): Payment status
        transportation_cost (float, optional): Transportation cost
        commission_paid (float, optional): Commission paid
        quality_grade (str, optional): Quality grade
        quality_notes (str, optional): Quality notes
        market_location (str, optional): Market location
        market_price_reference (float, optional): Reference market price
        notes (str, optional): Additional notes
        invoice_number (str, optional): Invoice number

    Returns:
        Dict[str, Any]: Result with updated sale information or error
    """
    db = get_db_session()

    try:
        # Find sale and verify ownership through crop
        sale = (
            db.query(Sale)
            .join(Crop)
            .filter(Sale.id == sale_id, Crop.user_id == user_id)
            .first()
        )

        if not sale:
            return {
                "status": "error",
                "error_message": f"Sale with ID {sale_id} not found or not owned by user {user_id}",
            }

        # Update fields if provided
        updates = {}

        if crop_type is not None:
            sale.crop_type = crop_type
            updates["crop_type"] = crop_type

        if crop_variety is not None:
            sale.crop_variety = crop_variety
            updates["crop_variety"] = crop_variety

        if quantity_kg is not None:
            sale.quantity_kg = quantity_kg
            updates["quantity_kg"] = quantity_kg

        if price_per_kg is not None:
            sale.price_per_kg = price_per_kg
            updates["price_per_kg"] = price_per_kg

        if total_amount is not None:
            sale.total_amount = total_amount
            updates["total_amount"] = total_amount
        elif quantity_kg is not None or price_per_kg is not None:
            # Recalculate total if quantity or price changed
            if sale.quantity_kg and sale.price_per_kg:
                sale.total_amount = sale.quantity_kg * sale.price_per_kg
                updates["total_amount"] = sale.total_amount

        if buyer_name is not None:
            sale.buyer_name = buyer_name
            updates["buyer_name"] = buyer_name

        if buyer_type is not None:
            sale.buyer_type = buyer_type
            updates["buyer_type"] = buyer_type

        if buyer_contact is not None:
            sale.buyer_contact = buyer_contact
            updates["buyer_contact"] = buyer_contact

        if payment_method is not None:
            sale.payment_method = payment_method
            updates["payment_method"] = payment_method

        if payment_status is not None:
            if payment_status in ["pending", "completed", "partial"]:
                sale.payment_status = payment_status
                updates["payment_status"] = payment_status
            else:
                return {
                    "status": "error",
                    "error_message": "payment_status must be 'pending', 'completed', or 'partial'",
                }

        if transportation_cost is not None:
            sale.transportation_cost = transportation_cost
            updates["transportation_cost"] = transportation_cost

        if commission_paid is not None:
            sale.commission_paid = commission_paid
            updates["commission_paid"] = commission_paid

        if quality_grade is not None:
            sale.quality_grade = quality_grade
            updates["quality_grade"] = quality_grade

        if quality_notes is not None:
            sale.quality_notes = quality_notes
            updates["quality_notes"] = quality_notes

        if market_location is not None:
            sale.market_location = market_location
            updates["market_location"] = market_location

        if market_price_reference is not None:
            sale.market_price_reference = market_price_reference
            updates["market_price_reference"] = market_price_reference

        if notes is not None:
            sale.notes = notes
            updates["notes"] = notes

        if invoice_number is not None:
            sale.invoice_number = invoice_number
            updates["invoice_number"] = invoice_number

        db.commit()
        db.refresh(sale)

        logging.info(f"Updated sale {sale_id} for user {user_id}")

        return {
            "status": "success",
            "sale_id": sale.id,
            "updates_applied": updates,
            "total_amount": sale.total_amount,
            "payment_status": sale.payment_status,
            "message": f"Successfully updated sale record",
        }

    except Exception as e:
        logging.error(f"Error updating sale: {str(e)}")
        return {"status": "error", "error_message": f"Failed to update sale: {str(e)}"}
    finally:
        db.close()


async def get_sales_tool(
    user_id: int,
    sale_id: Optional[int] = None,
    crop_id: Optional[int] = None,
    crop_type: Optional[str] = None,
    buyer_type: Optional[str] = None,
    payment_status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """
    Get sales information for a user.

    Args:
        user_id (int): User ID
        sale_id (int, optional): Specific sale ID to retrieve
        crop_id (int, optional): Filter by crop ID
        crop_type (str, optional): Filter by crop type
        buyer_type (str, optional): Filter by buyer type
        payment_status (str, optional): Filter by payment status
        start_date (str, optional): Start date filter (YYYY-MM-DD)
        end_date (str, optional): End date filter (YYYY-MM-DD)
        limit (int): Maximum number of sales to return (default: 20)

    Returns:
        Dict[str, Any]: Result with sales information or error
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

        # Build query - join with crops to ensure user ownership
        query = db.query(Sale).join(Crop).filter(Crop.user_id == user_id)

        if sale_id is not None:
            query = query.filter(Sale.id == sale_id)

        if crop_id is not None:
            query = query.filter(Sale.crop_id == crop_id)

        if crop_type is not None:
            query = query.filter(Sale.crop_type.ilike(f"%{crop_type}%"))

        if buyer_type is not None:
            query = query.filter(Sale.buyer_type == buyer_type)

        if payment_status is not None:
            query = query.filter(Sale.payment_status == payment_status)

        # Date range filters
        if start_date is not None:
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                query = query.filter(Sale.sale_date >= start_date_obj)
            except ValueError:
                return {
                    "status": "error",
                    "error_message": "Invalid start_date format. Use YYYY-MM-DD",
                }

        if end_date is not None:
            try:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                query = query.filter(Sale.sale_date <= end_date_obj)
            except ValueError:
                return {
                    "status": "error",
                    "error_message": "Invalid end_date format. Use YYYY-MM-DD",
                }

        # Execute query
        sales = query.order_by(Sale.sale_date.desc()).limit(limit).all()

        if not sales:
            return {
                "status": "success",
                "sales": [],
                "total_count": 0,
                "total_revenue": 0,
                "message": "No sales found matching the criteria",
            }

        # Format sales data and calculate totals
        sales_data = []
        total_revenue = 0
        total_quantity = 0

        for sale in sales:
            sale_info = {
                "sale_id": sale.id,
                "crop_id": sale.crop_id,
                "sale_date": sale.sale_date.isoformat(),
                "crop_type": sale.crop_type,
                "crop_variety": sale.crop_variety,
                "quantity_kg": sale.quantity_kg,
                "price_per_kg": sale.price_per_kg,
                "total_amount": sale.total_amount,
                "buyer_info": {
                    "buyer_name": sale.buyer_name,
                    "buyer_type": sale.buyer_type,
                    "buyer_contact": sale.buyer_contact,
                },
                "payment_info": {
                    "payment_method": sale.payment_method,
                    "payment_status": sale.payment_status,
                },
                "costs": {
                    "transportation_cost": sale.transportation_cost,
                    "commission_paid": sale.commission_paid,
                },
                "quality": {
                    "quality_grade": sale.quality_grade,
                    "quality_notes": sale.quality_notes,
                },
                "market_info": {
                    "market_location": sale.market_location,
                    "market_price_reference": sale.market_price_reference,
                },
                "notes": sale.notes,
                "invoice_number": sale.invoice_number,
                "created_at": sale.created_at.isoformat(),
                "updated_at": sale.updated_at.isoformat(),
            }
            sales_data.append(sale_info)

            # Calculate totals
            if sale.total_amount:
                total_revenue += sale.total_amount
            if sale.quantity_kg:
                total_quantity += sale.quantity_kg

        logging.info(f"Retrieved {len(sales)} sales for user {user_id}")

        return {
            "status": "success",
            "sales": sales_data,
            "total_count": len(sales_data),
            "summary": {
                "total_revenue": total_revenue,
                "total_quantity_kg": total_quantity,
                "average_price_per_kg": total_revenue / total_quantity
                if total_quantity > 0
                else 0,
            },
            "message": f"Found {len(sales_data)} sale(s) with total revenue of ₹{total_revenue:.2f}",
        }

    except Exception as e:
        logging.error(f"Error retrieving sales: {str(e)}")
        return {
            "status": "error",
            "error_message": f"Failed to retrieve sales: {str(e)}",
        }
    finally:
        db.close()


async def get_sales_analytics_tool(
    user_id: int,
    crop_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get sales analytics and insights for a user.

    Args:
        user_id (int): User ID
        crop_type (str, optional): Filter by crop type
        start_date (str, optional): Start date filter (YYYY-MM-DD)
        end_date (str, optional): End date filter (YYYY-MM-DD)

    Returns:
        Dict[str, Any]: Result with sales analytics or error
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

        # Build base query
        query = db.query(Sale).join(Crop).filter(Crop.user_id == user_id)

        if crop_type is not None:
            query = query.filter(Sale.crop_type.ilike(f"%{crop_type}%"))

        # Date range filters
        if start_date is not None:
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                query = query.filter(Sale.sale_date >= start_date_obj)
            except ValueError:
                return {
                    "status": "error",
                    "error_message": "Invalid start_date format. Use YYYY-MM-DD",
                }

        if end_date is not None:
            try:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                query = query.filter(Sale.sale_date <= end_date_obj)
            except ValueError:
                return {
                    "status": "error",
                    "error_message": "Invalid end_date format. Use YYYY-MM-DD",
                }

        # Get all sales for analytics
        sales = query.all()

        if not sales:
            return {
                "status": "success",
                "analytics": {
                    "total_sales": 0,
                    "total_revenue": 0,
                    "total_quantity_kg": 0,
                    "average_price_per_kg": 0,
                },
                "message": "No sales data found for analytics",
            }

        # Calculate analytics
        total_sales = len(sales)
        total_revenue = sum(sale.total_amount or 0 for sale in sales)
        total_quantity = sum(sale.quantity_kg or 0 for sale in sales)

        # Crop type breakdown
        crop_breakdown = {}
        buyer_type_breakdown = {}
        payment_status_breakdown = {}

        for sale in sales:
            # Crop type breakdown
            crop = sale.crop_type or "Unknown"
            if crop not in crop_breakdown:
                crop_breakdown[crop] = {"count": 0, "revenue": 0, "quantity": 0}
            crop_breakdown[crop]["count"] += 1
            crop_breakdown[crop]["revenue"] += sale.total_amount or 0
            crop_breakdown[crop]["quantity"] += sale.quantity_kg or 0

            # Buyer type breakdown
            buyer = sale.buyer_type or "Unknown"
            if buyer not in buyer_type_breakdown:
                buyer_type_breakdown[buyer] = {"count": 0, "revenue": 0}
            buyer_type_breakdown[buyer]["count"] += 1
            buyer_type_breakdown[buyer]["revenue"] += sale.total_amount or 0

            # Payment status breakdown
            status = sale.payment_status or "Unknown"
            if status not in payment_status_breakdown:
                payment_status_breakdown[status] = {"count": 0, "revenue": 0}
            payment_status_breakdown[status]["count"] += 1
            payment_status_breakdown[status]["revenue"] += sale.total_amount or 0

        analytics = {
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "total_quantity_kg": total_quantity,
            "average_price_per_kg": total_revenue / total_quantity
            if total_quantity > 0
            else 0,
            "crop_breakdown": crop_breakdown,
            "buyer_type_breakdown": buyer_type_breakdown,
            "payment_status_breakdown": payment_status_breakdown,
        }

        logging.info(f"Generated sales analytics for user {user_id}")

        return {
            "status": "success",
            "analytics": analytics,
            "message": f"Analytics generated for {total_sales} sales with total revenue of ₹{total_revenue:.2f}",
        }

    except Exception as e:
        logging.error(f"Error generating sales analytics: {str(e)}")
        return {
            "status": "error",
            "error_message": f"Failed to generate sales analytics: {str(e)}",
        }
    finally:
        db.close()


# Tool declarations for Gemini AI
CREATE_SALE_TOOL_DECLARATION = {
    "name": "create_sale_tool",
    "description": "Create a new sale record for farm produce",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "integer", "description": "User ID of the farmer"},
            "crop_id": {"type": "integer", "description": "Crop ID for the sale"},
            "sale_date": {
                "type": "string",
                "description": "Sale date in YYYY-MM-DD format (defaults to today)",
            },
            "crop_type": {"type": "string", "description": "Type of crop sold"},
            "crop_variety": {"type": "string", "description": "Variety of crop sold"},
            "quantity_kg": {"type": "number", "description": "Quantity sold in kg"},
            "price_per_kg": {"type": "number", "description": "Price per kg"},
            "total_amount": {"type": "number", "description": "Total sale amount"},
            "buyer_name": {"type": "string", "description": "Name of buyer"},
            "buyer_type": {
                "type": "string",
                "description": "Type of buyer (direct, market, middleman, export, online)",
            },
            "buyer_contact": {
                "type": "string",
                "description": "Buyer contact information",
            },
            "payment_method": {
                "type": "string",
                "description": "Payment method (cash, bank_transfer, cheque, upi)",
            },
            "payment_status": {
                "type": "string",
                "description": "Payment status (pending, completed, partial)",
            },
            "transportation_cost": {
                "type": "number",
                "description": "Transportation cost",
            },
            "commission_paid": {"type": "number", "description": "Commission paid"},
            "quality_grade": {
                "type": "string",
                "description": "Quality grade (A, B, C)",
            },
            "quality_notes": {"type": "string", "description": "Quality notes"},
            "market_location": {"type": "string", "description": "Market location"},
            "market_price_reference": {
                "type": "number",
                "description": "Reference market price",
            },
            "notes": {"type": "string", "description": "Additional notes"},
            "invoice_number": {"type": "string", "description": "Invoice number"},
        },
        "required": ["user_id", "crop_id"],
    },
}

UPDATE_SALE_TOOL_DECLARATION = {
    "name": "update_sale_tool",
    "description": "Update an existing sale record",
    "parameters": {
        "type": "object",
        "properties": {
            "sale_id": {"type": "integer", "description": "Sale ID to update"},
            "user_id": {"type": "integer", "description": "User ID for verification"},
            "crop_type": {"type": "string", "description": "Type of crop sold"},
            "crop_variety": {"type": "string", "description": "Variety of crop sold"},
            "quantity_kg": {"type": "number", "description": "Quantity sold in kg"},
            "price_per_kg": {"type": "number", "description": "Price per kg"},
            "total_amount": {"type": "number", "description": "Total sale amount"},
            "buyer_name": {"type": "string", "description": "Name of buyer"},
            "buyer_type": {"type": "string", "description": "Type of buyer"},
            "buyer_contact": {
                "type": "string",
                "description": "Buyer contact information",
            },
            "payment_method": {"type": "string", "description": "Payment method"},
            "payment_status": {"type": "string", "description": "Payment status"},
            "transportation_cost": {
                "type": "number",
                "description": "Transportation cost",
            },
            "commission_paid": {"type": "number", "description": "Commission paid"},
            "quality_grade": {"type": "string", "description": "Quality grade"},
            "quality_notes": {"type": "string", "description": "Quality notes"},
            "market_location": {"type": "string", "description": "Market location"},
            "market_price_reference": {
                "type": "number",
                "description": "Reference market price",
            },
            "notes": {"type": "string", "description": "Additional notes"},
            "invoice_number": {"type": "string", "description": "Invoice number"},
        },
        "required": ["sale_id", "user_id"],
    },
}

GET_SALES_TOOL_DECLARATION = {
    "name": "get_sales_tool",
    "description": "Retrieve sales information for a farmer",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "integer", "description": "User ID of the farmer"},
            "sale_id": {
                "type": "integer",
                "description": "Specific sale ID to retrieve",
            },
            "crop_id": {"type": "integer", "description": "Filter by crop ID"},
            "crop_type": {"type": "string", "description": "Filter by crop type"},
            "buyer_type": {"type": "string", "description": "Filter by buyer type"},
            "payment_status": {
                "type": "string",
                "description": "Filter by payment status",
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
                "description": "Maximum number of sales to return (default: 20)",
            },
        },
        "required": ["user_id"],
    },
}

GET_SALES_ANALYTICS_TOOL_DECLARATION = {
    "name": "get_sales_analytics_tool",
    "description": "Get sales analytics and insights for a farmer",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "integer", "description": "User ID of the farmer"},
            "crop_type": {"type": "string", "description": "Filter by crop type"},
            "start_date": {
                "type": "string",
                "description": "Start date filter in YYYY-MM-DD format",
            },
            "end_date": {
                "type": "string",
                "description": "End date filter in YYYY-MM-DD format",
            },
        },
        "required": ["user_id"],
    },
}
