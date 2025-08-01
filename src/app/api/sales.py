from __future__ import annotations

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..models.crop import Crop
from ..models.sale import Sale
from ..models.user import User
from ..schemas.sale import SaleCreate, SaleResponse, SaleUpdate
from ..utils.auth import get_current_user

router = APIRouter(prefix="/sales", tags=["sales"])


def verify_crop_ownership(crop_id: int, user_id: int, db: Session) -> Crop:
    """Verify that the user owns the crop."""
    crop = db.query(Crop).filter(Crop.id == crop_id, Crop.user_id == user_id).first()

    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Crop not found"
        )

    return crop


@router.post(
    "/crops/{crop_id}/sales",
    response_model=SaleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sale(
    crop_id: int,
    sale_data: SaleCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Sale:
    """Create a new sale record for a crop."""
    # Verify crop ownership
    verify_crop_ownership(crop_id, current_user.id, db)

    # Create sale
    db_sale = Sale(crop_id=crop_id, **sale_data.model_dump())

    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)

    return db_sale


@router.get("/crops/{crop_id}/sales", response_model=List[SaleResponse])
def get_crop_sales(
    crop_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
) -> List[Sale]:
    """Get all sales for a crop."""
    # Verify crop ownership
    verify_crop_ownership(crop_id, current_user.id, db)

    return (
        db.query(Sale)
        .filter(Sale.crop_id == crop_id)
        .order_by(Sale.sale_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/sales/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Sale:
    """Get a specific sale record."""
    sale = (
        db.query(Sale)
        .join(Crop)
        .filter(Sale.id == sale_id, Crop.user_id == current_user.id)
        .first()
    )

    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sale record not found"
        )

    return sale


@router.put("/sales/{sale_id}", response_model=SaleResponse)
def update_sale(
    sale_id: int,
    sale_update: SaleUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Sale:
    """Update a sale record."""
    sale = (
        db.query(Sale)
        .join(Crop)
        .filter(Sale.id == sale_id, Crop.user_id == current_user.id)
        .first()
    )

    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sale record not found"
        )

    # Update sale with provided data
    update_data = sale_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sale, field, value)

    db.commit()
    db.refresh(sale)

    return sale


@router.delete("/sales/{sale_id}")
def delete_sale(
    sale_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    """Delete a sale record."""
    sale = (
        db.query(Sale)
        .join(Crop)
        .filter(Sale.id == sale_id, Crop.user_id == current_user.id)
        .first()
    )

    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sale record not found"
        )

    db.delete(sale)
    db.commit()

    return {"message": "Sale record deleted successfully"}


@router.get("/", response_model=List[SaleResponse])
def get_user_sales(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
) -> List[Sale]:
    """Get all sales for the current user across all crops."""
    return (
        db.query(Sale)
        .join(Crop)
        .filter(Crop.user_id == current_user.id)
        .order_by(Sale.sale_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/analytics")
def get_sales_analytics(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """Get sales analytics for the current user."""
    # Get all user sales
    sales = db.query(Sale).join(Crop).filter(Crop.user_id == current_user.id).all()

    if not sales:
        return {
            "total_sales": 0,
            "total_revenue": 0.0,
            "average_price_per_kg": 0.0,
            "total_quantity_kg": 0.0,
            "total_transportation_cost": 0.0,
            "net_revenue": 0.0,
        }

    total_revenue = sum(sale.total_amount or 0 for sale in sales)
    total_quantity = sum(sale.quantity_kg or 0 for sale in sales)
    total_transportation_cost = sum(sale.transportation_cost or 0 for sale in sales)

    return {
        "total_sales": len(sales),
        "total_revenue": total_revenue,
        "average_price_per_kg": total_revenue / total_quantity
        if total_quantity > 0
        else 0,
        "total_quantity_kg": total_quantity,
        "total_transportation_cost": total_transportation_cost,
        "net_revenue": total_revenue - total_transportation_cost,
    }
