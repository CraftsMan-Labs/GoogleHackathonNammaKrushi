from google.adk.agents import Agent
import requests
from typing import Dict, Any
import requests
import os
from typing import Dict, Any
from google.adk.tools import google_search


def create_google_search_tool():
    """Provides Google Search tool via ADK"""
    return google_search


def get_current_weather(lat: float, lon: float) -> Dict[str, Any]:
    api_key = os.getenv("GOOGLE_WEATHER_API_KEY")
    endpoint = "https://maps.googleapis.com/maps/api/weather/v1/current"
    params = {"location": f"{lat},{lon}", "key": api_key}
    resp = requests.get(endpoint, params=params)
    if resp.status_code == 200:
        return resp.json()
    return {"error": "Weather API Error", "status_code": resp.status_code}


def get_soilgrids_data(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetches soil property data for the given latitude and longitude using the SoilGrids REST API.
    Returns surface (0-5cm) values for all soil properties.
    """
    url = f"https://rest.soilgrids.org/query?lon={lon}&lat={lat}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        soil_data = resp.json()
        surface_props = {}
        properties = soil_data.get("properties", {})
        for prop, v in properties.items():
            try:
                surface_val = v["values"][0]["mean"]
                surface_props[prop] = surface_val
            except Exception:
                continue
        return {
            "status": "success",
            "latitude": lat,
            "longitude": lon,
            "surface_soil_properties": surface_props,
            "soilgrids_raw": properties,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch SoilGrids data: {str(e)}",
        }


root_agent = Agent(
    name="multi_api_streaming_agent",
    model="gemini-2.5-flash",
    description=(
        "Expert assistant with access to Google Search, Location, Weather, and Soil Data APIs. "
        "Given a location (as name/address or lat/lon), can provide coordinates, weather, and full soil properties."
    ),
    instruction="""You are an advanced assistant for environmental and location data.
    - Given a user-input location (address or latitude/longitude), you can fetch coordinates, current weather,
      and a detailed set of soil properties for that point using SoilGrids.
    - For soil properties, call the 'get_soilgrids_data' tool when lat/lon are specified.
    - Respond with clear, concise information and highlight key findings (such as soil pH, nitrogen, sand/clay content, etc).
    """,
    tools=[create_google_search_tool, get_current_weather, get_soilgrids_data],
)
