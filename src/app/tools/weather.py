"""
Weather Tools for Agricultural Assistant

Provides weather information using OpenWeatherMap API for farming decisions.
"""

import os
import logging
import requests
from typing import Dict, Any


async def get_weather_by_location(city: str) -> Dict[str, Any]:
    """
    Retrieves the current weather report for a specified city using OpenWeatherMap API.

    Args:
        city (str): The city name for weather information

    Returns:
        Dict[str, Any]: Weather data with status and formatted report
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return {
            "status": "error",
            "error_message": "OpenWeather API key not configured",
        }

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        weather_info = {
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "city": data["name"],
            "country": data["sys"]["country"],
        }

        return {
            "status": "success",
            "weather_data": weather_info,
            "report": f"Weather in {data['name']}, {data['sys']['country']}: {data['weather'][0]['description']}, {data['main']['temp']}°C, Humidity: {data['main']['humidity']}%",
        }
    except Exception as e:
        logging.error(f"Weather API request failed for city {city}: {str(e)}")
        return {
            "status": "error",
            "error_message": f"Weather API request failed: {str(e)}",
        }


async def get_weather_by_coordinates(lat: float, lon: float) -> Dict[str, Any]:
    """
    Retrieves current weather data for specified coordinates.

    Args:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate

    Returns:
        Dict[str, Any]: Weather data with status
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return {
            "status": "error",
            "error_message": "OpenWeather API key not configured",
        }

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        return {"status": "success", "weather_data": data}
    except Exception as e:
        logging.error(
            f"Weather API request failed for coordinates {lat}, {lon}: {str(e)}"
        )
        return {
            "status": "error",
            "error_message": f"Weather API request failed: {str(e)}",
        }


# Tool declarations for Gemini AI
WEATHER_LOCATION_TOOL_DECLARATION = {
    "name": "get_weather_by_location",
    "description": "Gets current weather for a specified city to help with farming decisions",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "The city name for weather information",
            }
        },
        "required": ["city"],
    },
}

WEATHER_COORDINATES_TOOL_DECLARATION = {
    "name": "get_weather_by_coordinates",
    "description": "Gets current weather for specified coordinates to help with farming decisions",
    "parameters": {
        "type": "object",
        "properties": {
            "lat": {"type": "number", "description": "Latitude coordinate"},
            "lon": {"type": "number", "description": "Longitude coordinate"},
        },
        "required": ["lat", "lon"],
    },
}
