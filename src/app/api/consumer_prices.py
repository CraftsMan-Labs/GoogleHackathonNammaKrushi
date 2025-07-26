from __future__ import annotations

from typing import Annotated, List
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..config.database import get_db
from ..models.consumer_price import ConsumerPrice
from ..models.user import User
from ..schemas.consumer_price import ConsumerPriceCreate, ConsumerPriceResponse, ConsumerPriceUpdate
from ..utils.auth import get_current_user

router = APIRouter(prefix="/consumer-prices", tags=["consumer-prices"])


@router.post(
    "/",
    response_model=ConsumerPriceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_consumer_price(
    price_data: ConsumerPriceCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ConsumerPrice:
    """Create a new consumer price record."""
    db_price = ConsumerPrice(**price_data.model_dump())

    db.add(db_price)
    db.commit()
    db.refresh(db_price)

    return db_price


@router.get("/", response_model=List[ConsumerPriceResponse])
def get_consumer_prices(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 100,
    crop_type: str = Query(None, description="Filter by crop type"),
    market_location: str = Query(None, description="Filter by market location"),
    start_date: date = Query(None, description="Filter prices from this date"),
    end_date: date = Query(None, description="Filter prices until this date"),
) -> List[ConsumerPrice]:
    """Get consumer price records with optional filters."""
    query = db.query(ConsumerPrice)
    
    if crop_type:
        query = query.filter(ConsumerPrice.crop_type.ilike(f"%{crop_type}%"))
    
    if market_location:
        query = query.filter(ConsumerPrice.market_location.ilike(f"%{market_location}%"))
    
    if start_date:
        query = query.filter(ConsumerPrice.price_date >= start_date)
    
    if end_date:
        query = query.filter(ConsumerPrice.price_date <= end_date)

    return (
        query
        .order_by(ConsumerPrice.price_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{price_id}", response_model=ConsumerPriceResponse)
def get_consumer_price(
    price_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ConsumerPrice:
    """Get a specific consumer price record."""
    price = db.query(ConsumerPrice).filter(ConsumerPrice.id == price_id).first()

    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Consumer price record not found"
        )

    return price


@router.put("/{price_id}", response_model=ConsumerPriceResponse)
def update_consumer_price(
    price_id: int,
    price_update: ConsumerPriceUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ConsumerPrice:
    """Update a consumer price record."""
    price = db.query(ConsumerPrice).filter(ConsumerPrice.id == price_id).first()

    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Consumer price record not found"
        )

    # Update price with provided data
    update_data = price_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(price, field, value)

    db.commit()
    db.refresh(price)

    return price


@router.delete("/{price_id}")
def delete_consumer_price(
    price_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    """Delete a consumer price record."""
    price = db.query(ConsumerPrice).filter(ConsumerPrice.id == price_id).first()

    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Consumer price record not found"
        )

    db.delete(price)
    db.commit()

    return {"message": "Consumer price record deleted successfully"}


@router.get("/analytics/summary")
def get_price_analytics(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    crop_type: str = Query(None, description="Filter analytics by crop type"),
    market_location: str = Query(None, description="Filter analytics by market location"),
) -> dict:
    """Get price analytics and summary statistics."""
    query = db.query(ConsumerPrice)
    
    if crop_type:
        query = query.filter(ConsumerPrice.crop_type.ilike(f"%{crop_type}%"))
    
    if market_location:
        query = query.filter(ConsumerPrice.market_location.ilike(f"%{market_location}%"))
    
    prices = query.all()

    if not prices:
        return {
            "total_records": 0,
            "average_price": 0.0,
            "min_price": 0.0,
            "max_price": 0.0,
            "price_range": 0.0,
            "unique_crops": 0,
            "unique_markets": 0,
        }

    price_values = [p.price_per_kg for p in prices]
    
    return {
        "total_records": len(prices),
        "average_price": sum(price_values) / len(price_values),
        "min_price": min(price_values),
        "max_price": max(price_values),
        "price_range": max(price_values) - min(price_values),
        "unique_crops": len(set(p.crop_type for p in prices)),
        "unique_markets": len(set(p.market_location for p in prices)),
    }


@router.get("/analytics/trends")
def get_price_trends(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    crop_type: str = Query(..., description="Crop type for trend analysis"),
    market_location: str = Query(None, description="Market location for trend analysis"),
    days: int = Query(30, description="Number of days for trend analysis"),
) -> dict:
    """Get price trends for a specific crop over time."""
    from datetime import timedelta
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    query = db.query(ConsumerPrice).filter(
        ConsumerPrice.crop_type.ilike(f"%{crop_type}%"),
        ConsumerPrice.price_date >= start_date,
        ConsumerPrice.price_date <= end_date
    )
    
    if market_location:
        query = query.filter(ConsumerPrice.market_location.ilike(f"%{market_location}%"))
    
    prices = query.order_by(ConsumerPrice.price_date).all()
    
    if not prices:
        return {
            "crop_type": crop_type,
            "market_location": market_location,
            "period_days": days,
            "data_points": 0,
            "trend": "no_data",
            "price_history": []
        }
    
    # Calculate trend
    price_values = [p.price_per_kg for p in prices]
    if len(price_values) > 1:
        first_half_avg = sum(price_values[:len(price_values)//2]) / (len(price_values)//2)
        second_half_avg = sum(price_values[len(price_values)//2:]) / (len(price_values) - len(price_values)//2)
        
        if second_half_avg > first_half_avg * 1.05:
            trend = "increasing"
        elif second_half_avg < first_half_avg * 0.95:
            trend = "decreasing"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"
    
    return {
        "crop_type": crop_type,
        "market_location": market_location,
        "period_days": days,
        "data_points": len(prices),
        "trend": trend,
        "average_price": sum(price_values) / len(price_values),
        "price_history": [
            {
                "date": p.price_date.isoformat(),
                "price": p.price_per_kg,
                "market": p.market_location,
                "quality": p.quality_grade
            }
            for p in prices
        ]
    }


@router.get("/analytics/location-trends")
def get_location_based_trends(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    crop_type: str = Query(..., description="Crop type for location analysis"),
    days: int = Query(30, description="Number of days for analysis"),
) -> dict:
    """Get location-based price trends and regional comparisons."""
    from datetime import timedelta
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Get all prices for the crop within date range
    prices = db.query(ConsumerPrice).filter(
        ConsumerPrice.crop_type.ilike(f"%{crop_type}%"),
        ConsumerPrice.price_date >= start_date,
        ConsumerPrice.price_date <= end_date
    ).all()
    
    if not prices:
        return {
            "crop_type": crop_type,
            "period_days": days,
            "total_markets": 0,
            "regional_analysis": [],
            "price_spread": {
                "min_market": None,
                "max_market": None,
                "price_difference": 0.0
            }
        }
    
    # Group by market location
    market_data = {}
    for price in prices:
        market = price.market_location
        if market not in market_data:
            market_data[market] = {
                "prices": [],
                "source_regions": set(),
                "transport_distances": [],
                "market_types": set(),
                "availability_statuses": [],
                "demand_levels": []
            }
        
        market_data[market]["prices"].append(price.price_per_kg)
        if price.source_region:
            market_data[market]["source_regions"].add(price.source_region)
        if price.transportation_distance_km:
            market_data[market]["transport_distances"].append(price.transportation_distance_km)
        if price.market_type:
            market_data[market]["market_types"].add(price.market_type)
        if price.availability_status:
            market_data[market]["availability_statuses"].append(price.availability_status)
        if price.demand_level:
            market_data[market]["demand_levels"].append(price.demand_level)
    
    # Calculate regional analysis
    regional_analysis = []
    min_price_market = None
    max_price_market = None
    min_avg_price = float('inf')
    max_avg_price = 0.0
    
    for market, data in market_data.items():
        avg_price = sum(data["prices"]) / len(data["prices"])
        min_price = min(data["prices"])
        max_price = max(data["prices"])
        
        # Track overall min/max markets
        if avg_price < min_avg_price:
            min_avg_price = avg_price
            min_price_market = market
        if avg_price > max_avg_price:
            max_avg_price = avg_price
            max_price_market = market
        
        # Calculate average transport distance
        avg_transport_distance = (
            sum(data["transport_distances"]) / len(data["transport_distances"])
            if data["transport_distances"] else None
        )
        
        # Most common availability and demand
        most_common_availability = (
            max(set(data["availability_statuses"]), key=data["availability_statuses"].count)
            if data["availability_statuses"] else None
        )
        most_common_demand = (
            max(set(data["demand_levels"]), key=data["demand_levels"].count)
            if data["demand_levels"] else None
        )
        
        regional_analysis.append({
            "market_location": market,
            "average_price": round(avg_price, 2),
            "min_price": round(min_price, 2),
            "max_price": round(max_price, 2),
            "price_volatility": round(max_price - min_price, 2),
            "data_points": len(data["prices"]),
            "source_regions": list(data["source_regions"]),
            "market_types": list(data["market_types"]),
            "avg_transport_distance_km": round(avg_transport_distance, 2) if avg_transport_distance else None,
            "common_availability": most_common_availability,
            "common_demand": most_common_demand
        })
    
    # Sort by average price
    regional_analysis.sort(key=lambda x: x["average_price"])
    
    return {
        "crop_type": crop_type,
        "period_days": days,
        "total_markets": len(market_data),
        "regional_analysis": regional_analysis,
        "price_spread": {
            "min_market": min_price_market,
            "min_price": round(min_avg_price, 2),
            "max_market": max_price_market,
            "max_price": round(max_avg_price, 2),
            "price_difference": round(max_avg_price - min_avg_price, 2)
        }
    }


@router.get("/analytics/nearby-markets")
def get_nearby_markets_analysis(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    crop_type: str = Query(..., description="Crop type for analysis"),
    user_location: str = Query(..., description="User's location for proximity analysis"),
    max_distance_km: float = Query(100, description="Maximum distance in km"),
) -> dict:
    """Get analysis of nearby markets for supply chain optimization."""
    
    # Get all recent prices for the crop (last 7 days)
    from datetime import timedelta
    recent_date = date.today() - timedelta(days=7)
    
    prices = db.query(ConsumerPrice).filter(
        ConsumerPrice.crop_type.ilike(f"%{crop_type}%"),
        ConsumerPrice.price_date >= recent_date
    ).all()
    
    if not prices:
        return {
            "crop_type": crop_type,
            "user_location": user_location,
            "max_distance_km": max_distance_km,
            "nearby_markets": [],
            "recommendations": []
        }
    
    # Filter by transportation distance if available
    nearby_markets = []
    for price in prices:
        if (price.transportation_distance_km and 
            price.transportation_distance_km <= max_distance_km):
            
            nearby_markets.append({
                "market_location": price.market_location,
                "distance_km": price.transportation_distance_km,
                "price_per_kg": price.price_per_kg,
                "market_type": price.market_type,
                "vendor_name": price.vendor_name,
                "availability_status": price.availability_status,
                "demand_level": price.demand_level,
                "quality_grade": price.quality_grade,
                "price_date": price.price_date.isoformat()
            })
    
    # Sort by price (highest first for selling opportunities)
    nearby_markets.sort(key=lambda x: x["price_per_kg"], reverse=True)
    
    # Generate recommendations
    recommendations = []
    if nearby_markets:
        best_price_market = nearby_markets[0]
        recommendations.append({
            "type": "best_price",
            "message": f"Highest price found at {best_price_market['market_location']} - ₹{best_price_market['price_per_kg']}/kg",
            "market": best_price_market['market_location'],
            "price": best_price_market['price_per_kg'],
            "distance": best_price_market['distance_km']
        })
        
        # Find closest market
        closest_market = min(nearby_markets, key=lambda x: x["distance_km"])
        if closest_market != best_price_market:
            recommendations.append({
                "type": "closest_market",
                "message": f"Closest market: {closest_market['market_location']} - ₹{closest_market['price_per_kg']}/kg ({closest_market['distance_km']}km)",
                "market": closest_market['market_location'],
                "price": closest_market['price_per_kg'],
                "distance": closest_market['distance_km']
            })
        
        # High demand markets
        high_demand_markets = [m for m in nearby_markets if m.get('demand_level') == 'high']
        if high_demand_markets:
            best_demand_market = max(high_demand_markets, key=lambda x: x["price_per_kg"])
            recommendations.append({
                "type": "high_demand",
                "message": f"High demand at {best_demand_market['market_location']} - ₹{best_demand_market['price_per_kg']}/kg",
                "market": best_demand_market['market_location'],
                "price": best_demand_market['price_per_kg'],
                "distance": best_demand_market['distance_km']
            })
    
    return {
        "crop_type": crop_type,
        "user_location": user_location,
        "max_distance_km": max_distance_km,
        "nearby_markets": nearby_markets,
        "total_markets_found": len(nearby_markets),
        "recommendations": recommendations
    }


@router.get("/analytics/regional-comparison")
def get_regional_price_comparison(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    crop_type: str = Query(..., description="Crop type for comparison"),
    regions: str = Query(..., description="Comma-separated list of regions to compare"),
    days: int = Query(30, description="Number of days for analysis"),
) -> dict:
    """Compare prices across different regions for supply chain planning."""
    from datetime import timedelta
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    region_list = [r.strip() for r in regions.split(',')]
    
    # Get prices for specified regions
    prices = db.query(ConsumerPrice).filter(
        ConsumerPrice.crop_type.ilike(f"%{crop_type}%"),
        ConsumerPrice.price_date >= start_date,
        ConsumerPrice.price_date <= end_date
    ).all()
    
    # Filter prices by regions (check both market_location and source_region)
    regional_prices = {}
    for region in region_list:
        regional_prices[region] = []
        
    for price in prices:
        for region in region_list:
            if (region.lower() in (price.market_location or "").lower() or 
                region.lower() in (price.source_region or "").lower()):
                regional_prices[region].append(price)
    
    # Calculate comparison data
    comparison_data = []
    for region, region_prices in regional_prices.items():
        if not region_prices:
            comparison_data.append({
                "region": region,
                "data_available": False,
                "message": "No data available for this region"
            })
            continue
            
        price_values = [p.price_per_kg for p in region_prices]
        avg_price = sum(price_values) / len(price_values)
        
        # Calculate trend
        if len(price_values) > 1:
            recent_prices = price_values[-len(price_values)//2:] if len(price_values) > 2 else price_values[-1:]
            older_prices = price_values[:len(price_values)//2] if len(price_values) > 2 else price_values[:1]
            
            recent_avg = sum(recent_prices) / len(recent_prices)
            older_avg = sum(older_prices) / len(older_prices)
            
            if recent_avg > older_avg * 1.05:
                trend = "increasing"
            elif recent_avg < older_avg * 0.95:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Market characteristics
        market_types = list(set(p.market_type for p in region_prices if p.market_type))
        avg_transport_distance = None
        transport_distances = [p.transportation_distance_km for p in region_prices if p.transportation_distance_km]
        if transport_distances:
            avg_transport_distance = sum(transport_distances) / len(transport_distances)
        
        comparison_data.append({
            "region": region,
            "data_available": True,
            "average_price": round(avg_price, 2),
            "min_price": round(min(price_values), 2),
            "max_price": round(max(price_values), 2),
            "price_trend": trend,
            "data_points": len(region_prices),
            "market_types": market_types,
            "avg_transport_distance_km": round(avg_transport_distance, 2) if avg_transport_distance else None,
            "unique_markets": len(set(p.market_location for p in region_prices))
        })
    
    # Sort by average price
    available_data = [d for d in comparison_data if d["data_available"]]
    available_data.sort(key=lambda x: x["average_price"], reverse=True)
    
    # Generate insights
    insights = []
    if len(available_data) >= 2:
        highest_region = available_data[0]
        lowest_region = available_data[-1]
        
        price_gap = highest_region["average_price"] - lowest_region["average_price"]
        insights.append({
            "type": "price_gap",
            "message": f"Price difference of ₹{price_gap:.2f}/kg between {highest_region['region']} (₹{highest_region['average_price']}/kg) and {lowest_region['region']} (₹{lowest_region['average_price']}/kg)"
        })
        
        # Transport cost analysis
        if (highest_region.get("avg_transport_distance_km") and 
            lowest_region.get("avg_transport_distance_km")):
            transport_diff = abs(highest_region["avg_transport_distance_km"] - lowest_region["avg_transport_distance_km"])
            insights.append({
                "type": "transport_analysis",
                "message": f"Transport distance difference: {transport_diff:.1f}km between regions"
            })
    
    return {
        "crop_type": crop_type,
        "regions_analyzed": region_list,
        "period_days": days,
        "regional_comparison": comparison_data,
        "insights": insights
    }