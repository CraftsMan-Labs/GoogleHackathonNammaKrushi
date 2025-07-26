from __future__ import annotations

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..models.user import User
from ..models.weather import WeatherHistory
from ..schemas.weather import WeatherCreate, WeatherResponse
from ..utils.auth import get_current_user

router = APIRouter(prefix="/weather", tags=["weather"])


def generate_mock_weather_data(user: User) -> dict:
    """Generate mock weather data for demo purposes."""
    # In production, this would call actual weather APIs
    return {
        "temperature": 28.5,
        "feels_like": 32.0,
        "humidity": 65.0,
        "pressure": 1013.2,
        "visibility": 10.0,
        "uv_index": 7.0,
        "rainfall": 0.0,
        "rainfall_probability": 30.0,
        "wind_speed": 12.0,
        "wind_direction": "SW",
        "wind_gust": 18.0,
        "conditions": "partly_cloudy",
        "weather_description": "Partly cloudy with scattered clouds",
        "location_name": user.location or "Karnataka",
        "latitude": user.latitude or 12.9716,
        "longitude": user.longitude or 77.5946,
        "alerts": "No weather alerts",
        "recommended_actions": "Good day for farming activities. Consider irrigation if no rain expected.",
        "crop_impact_assessment": "Favorable conditions for most crops",
        "irrigation_recommendation": "Light irrigation recommended",
        "pest_disease_risk": "low"
    }


@router.post("/", response_model=WeatherResponse, status_code=status.HTTP_201_CREATED)
def create_weather_record(
    weather_data: WeatherCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
) -> WeatherHistory:
    """Create a new weather record."""
    db_weather = WeatherHistory(
        user_id=current_user.id,
        **weather_data.model_dump()
    )
    
    db.add(db_weather)
    db.commit()
    db.refresh(db_weather)
    
    return db_weather


@router.get("/current", response_model=WeatherResponse)
def get_current_weather(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
) -> WeatherHistory:
    """Get current weather for user's location."""
    # Check if we have recent weather data (within last 2 hours)
    from datetime import datetime, timedelta
    recent_weather = db.query(WeatherHistory).filter(
        WeatherHistory.user_id == current_user.id,
        WeatherHistory.is_forecast == False,
        WeatherHistory.created_at >= datetime.utcnow() - timedelta(hours=2)
    ).order_by(WeatherHistory.created_at.desc()).first()
    
    if recent_weather:
        return recent_weather
    
    # Generate new weather data
    weather_data = generate_mock_weather_data(current_user)
    
    db_weather = WeatherHistory(
        user_id=current_user.id,
        **weather_data
    )
    
    db.add(db_weather)
    db.commit()
    db.refresh(db_weather)
    
    return db_weather


@router.get("/forecast", response_model=List[WeatherResponse])
def get_weather_forecast(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    days: int = 7
) -> List[WeatherHistory]:
    """Get weather forecast for the next few days."""
    if days > 7:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Forecast limited to 7 days"
        )
    
    # Check if we have recent forecast data
    from datetime import datetime, timedelta
    recent_forecast = db.query(WeatherHistory).filter(
        WeatherHistory.user_id == current_user.id,
        WeatherHistory.is_forecast == True,
        WeatherHistory.created_at >= datetime.utcnow() - timedelta(hours=6)
    ).order_by(WeatherHistory.forecast_days_ahead).limit(days).all()
    
    if len(recent_forecast) >= days:
        return recent_forecast
    
    # Generate forecast data
    forecast_data = []
    base_weather = generate_mock_weather_data(current_user)
    
    for day in range(1, days + 1):
        # Simulate weather variations
        temp_variation = (-2 + (day % 3)) * 1.5
        humidity_variation = (-5 + (day % 4)) * 2
        
        forecast_weather = WeatherHistory(
            user_id=current_user.id,
            date=datetime.utcnow().date() + timedelta(days=day),
            temperature=base_weather["temperature"] + temp_variation,
            feels_like=base_weather["feels_like"] + temp_variation,
            humidity=max(30, min(90, base_weather["humidity"] + humidity_variation)),
            pressure=base_weather["pressure"] + (day % 2) * 2,
            rainfall=max(0, (day % 3) * 2.5),
            rainfall_probability=min(80, base_weather["rainfall_probability"] + (day % 4) * 10),
            wind_speed=base_weather["wind_speed"] + (day % 2) * 3,
            conditions=base_weather["conditions"],
            weather_description=f"Day {day} forecast: {base_weather['weather_description']}",
            location_name=base_weather["location_name"],
            latitude=base_weather["latitude"],
            longitude=base_weather["longitude"],
            is_forecast=True,
            forecast_days_ahead=day,
            recommended_actions=f"Day {day}: Plan activities based on conditions",
            pest_disease_risk="medium" if day % 2 == 0 else "low"
        )
        
        db.add(forecast_weather)
        forecast_data.append(forecast_weather)
    
    db.commit()
    
    return forecast_data


@router.get("/history", response_model=List[WeatherResponse])
def get_weather_history(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    skip: int = 0,
    limit: int = 30
) -> List[WeatherHistory]:
    """Get weather history for the user."""
    return db.query(WeatherHistory).filter(
        WeatherHistory.user_id == current_user.id,
        WeatherHistory.is_forecast == False
    ).order_by(WeatherHistory.date.desc()).offset(skip).limit(limit).all()


@router.get("/{weather_id}", response_model=WeatherResponse)
def get_weather_record(
    weather_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
) -> WeatherHistory:
    """Get a specific weather record."""
    weather = db.query(WeatherHistory).filter(
        WeatherHistory.id == weather_id,
        WeatherHistory.user_id == current_user.id
    ).first()
    
    if not weather:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weather record not found"
        )
    
    return weather


@router.delete("/{weather_id}")
def delete_weather_record(
    weather_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
) -> dict[str, str]:
    """Delete a weather record."""
    weather = db.query(WeatherHistory).filter(
        WeatherHistory.id == weather_id,
        WeatherHistory.user_id == current_user.id
    ).first()
    
    if not weather:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weather record not found"
        )
    
    db.delete(weather)
    db.commit()
    
    return {"message": "Weather record deleted successfully"}