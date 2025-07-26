import logging
from google.adk.agents import Agent
import requests
from typing import Dict, Any, Union
import os
from dotenv import load_dotenv
from PIL import Image
import io
import base64

load_dotenv()


def google_search(query: str) -> dict:
    """Performs a Google search and returns a list of results.

    Args:
        query (str): The search query string.

    Returns:
        dict: status and search results or error message.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": os.getenv("GOOGLE_WEATHER_API_KEY"),
        "cx": os.getenv("GOOGLE_SEARCH_CSE_ID"),
        "num": 10,
    }

    try:
        logging.info(f"Performing Google search with params: {params}")
        response = requests.get(url, params=params)
        response.raise_for_status()

        results = response.json().get("items", [])

        search_results = [
            {
                "title": item.get("title"),
                "snippet": item.get("snippet"),
                "link": item.get("link"),
            }
            for item in results
        ]

        if search_results:
            formatted_results = "\n".join(
                f"{i + 1}. {item['title']}\n{item['snippet']}\n{item['link']}"
                for i, item in enumerate(search_results)
            )
            return {"status": "success", "results": formatted_results}
        else:
            return {"status": "success", "results": "No results found."}

    except Exception as e:
        return {"status": "error", "error_message": f"Google search failed: {str(e)}"}


def analyze_crop_image_and_search(
    image_input: Union[str, bytes, Image.Image],
    farmer_query: str,
    include_visual_search: bool = True,
) -> Dict[str, Any]:
    """
    Analyzes a diseased crop image using Google Vision API and performs a web search
    combining visual analysis with the farmer's query.

    Args:
        image_input: Can be a file path (str), raw bytes, or PIL Image object
        farmer_query: The farmer's description or question about the crop disease
        include_visual_search: Whether to include Google Lens reverse image search

    Returns:
        dict: Contains image analysis, search results, and recommendations
    """

    # Step 1: Prepare the image
    try:
        if isinstance(image_input, str):
            # File path provided
            with open(image_input, "rb") as img_file:
                image_bytes = img_file.read()
        elif isinstance(image_input, Image.Image):
            # PIL Image provided
            buffer = io.BytesIO()
            image_input.save(buffer, format="JPEG")
            image_bytes = buffer.getvalue()
        else:
            # Assume bytes
            image_bytes = image_input

        # Encode image to base64
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to process image: {str(e)}",
        }

    # Step 2: Analyze image with Google Vision API
    vision_analysis = {}
    try:
        vision_api_key = os.getenv("GOOGLE_CLOUD_API_KEY") or os.getenv(
            "GOOGLE_WEATHER_API_KEY"
        )
        vision_url = "https://vision.googleapis.com/v1/images:annotate"

        vision_request = {
            "requests": [
                {
                    "image": {"content": image_base64},
                    "features": [
                        {"type": "LABEL_DETECTION", "maxResults": 10},
                        {"type": "WEB_DETECTION", "maxResults": 5},
                        {"type": "OBJECT_LOCALIZATION", "maxResults": 5},
                        {"type": "IMAGE_PROPERTIES", "maxResults": 5},
                    ],
                }
            ]
        }

        vision_response = requests.post(
            f"{vision_url}?key={vision_api_key}", json=vision_request
        )
        vision_response.raise_for_status()
        vision_data = vision_response.json()

        if "responses" in vision_data and vision_data["responses"]:
            response = vision_data["responses"][0]

            # Extract labels (general image content)
            labels = []
            if "labelAnnotations" in response:
                labels = [
                    label["description"] for label in response["labelAnnotations"][:5]
                ]

            # Extract web entities (what Google thinks this is)
            web_entities = []
            if "webDetection" in response and "webEntities" in response["webDetection"]:
                web_entities = [
                    entity.get("description", "")
                    for entity in response["webDetection"]["webEntities"]
                    if entity.get("description")
                ][:3]

            # Extract dominant colors (useful for disease identification)
            dominant_colors = []
            if "imagePropertiesAnnotation" in response:
                colors = (
                    response["imagePropertiesAnnotation"]
                    .get("dominantColors", {})
                    .get("colors", [])
                )
                dominant_colors = [
                    {"rgb": color["color"], "score": color.get("score", 0)}
                    for color in colors[:3]
                ]

            vision_analysis = {
                "labels": labels,
                "web_entities": web_entities,
                "dominant_colors": dominant_colors,
                "visual_matches": response.get("webDetection", {}).get(
                    "visuallySimilarImages", []
                ),
            }

    except Exception as e:
        logging.error(f"Vision API error: {str(e)}")
        vision_analysis = {"error": f"Vision API failed: {str(e)}"}

    # Step 3: Construct enhanced search query
    search_terms = []

    # Add identified entities from vision API
    if vision_analysis.get("web_entities"):
        search_terms.extend(vision_analysis["web_entities"][:2])

    # Add relevant labels that might indicate crop or disease
    crop_disease_keywords = [
        "plant",
        "leaf",
        "disease",
        "fungus",
        "pest",
        "crop",
        "blight",
        "wilt",
        "spot",
    ]
    if vision_analysis.get("labels"):
        relevant_labels = [
            label
            for label in vision_analysis["labels"]
            if any(keyword in label.lower() for keyword in crop_disease_keywords)
        ]
        search_terms.extend(relevant_labels[:2])

    # Add farmer's query
    search_terms.append(farmer_query)

    # Combine into search query
    enhanced_query = " ".join(search_terms)

    # If no vision data, fall back to farmer query + generic terms
    if not search_terms[:-1]:  # If only farmer query remains
        enhanced_query = f"crop disease {farmer_query}"

    logging.info(f"Enhanced search query: {enhanced_query}")

    # Step 4: Perform Google Custom Search
    search_results = {}
    try:
        search_url = "https://www.googleapis.com/customsearch/v1"
        search_params = {
            "q": enhanced_query,
            "key": os.getenv("GOOGLE_WEATHER_API_KEY"),
            "cx": os.getenv("GOOGLE_SEARCH_CSE_ID"),
            "num": 10,
            "searchType": "image"
            if include_visual_search
            else None,  # Optional: search for similar images
        }

        # Remove None values
        search_params = {k: v for k, v in search_params.items() if v is not None}

        search_response = requests.get(search_url, params=search_params)
        search_response.raise_for_status()

        items = search_response.json().get("items", [])

        if items:
            formatted_results = []
            for i, item in enumerate(items):
                result = {
                    "rank": i + 1,
                    "title": item.get("title"),
                    "snippet": item.get("snippet"),
                    "link": item.get("link"),
                    "source": item.get("displayLink", ""),
                }
                formatted_results.append(result)

            search_results = {
                "status": "success",
                "query_used": enhanced_query,
                "results": formatted_results,
            }
        else:
            search_results = {
                "status": "success",
                "query_used": enhanced_query,
                "results": [],
            }

    except Exception as e:
        search_results = {
            "status": "error",
            "error_message": f"Search failed: {str(e)}",
        }

    # Step 5: Compile comprehensive response
    return {
        "status": "success",
        "farmer_query": farmer_query,
        "image_analysis": vision_analysis,
        "search_results": search_results,
        "recommendations": generate_recommendations(vision_analysis, search_results),
        "enhanced_query": enhanced_query,
    }


def generate_recommendations(vision_analysis: Dict, search_results: Dict) -> list:
    """Generate actionable recommendations based on analysis"""
    recommendations = []

    # Check if disease-related terms were detected
    if vision_analysis.get("labels"):
        disease_indicators = ["disease", "fungus", "pest", "damage", "infected"]
        detected_issues = [
            label
            for label in vision_analysis.get("labels", [])
            if any(indicator in label.lower() for indicator in disease_indicators)
        ]

        if detected_issues:
            recommendations.append(
                f"Potential issues detected: {', '.join(detected_issues)}"
            )
            recommendations.append(
                "Consider consulting with local agricultural extension office"
            )

    # Add color-based recommendations
    if vision_analysis.get("dominant_colors"):
        # This is simplified - in reality, you'd have more sophisticated analysis
        recommendations.append(
            "Document the progression of symptoms with regular photos"
        )

    # Add search-based recommendations
    if search_results.get("status") == "success" and search_results.get("results"):
        recommendations.append(
            f"Found {len(search_results['results'])} relevant resources"
        )
        recommendations.append(
            "Review top search results for similar cases and treatment options"
        )

    return recommendations


def get_current_weather(lat: float, lon: float) -> dict:
    """Retrieves current weather data for specified coordinates.

    Args:
        lat (float): Latitude coordinate.
        lon (float): Longitude coordinate.

    Returns:
        dict: status and weather data or error message.
    """
    api_key = os.getenv("GOOGLE_WEATHER_API_KEY")
    endpoint = "https://maps.googleapis.com/maps/api/weather/v1/current"
    params = {"location": f"{lat},{lon}", "key": api_key}

    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()

        weather_data = response.json()
        return {"status": "success", "weather_data": weather_data}

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Weather API request failed: {str(e)}",
        }


def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }


def get_soilgrids_data(lat: float, lon: float) -> dict:
    """Fetches soil property data for the given coordinates using the SoilGrids v2.0 REST API.

    Args:
        lat (float): Latitude coordinate.
        lon (float): Longitude coordinate.

    Returns:
        dict: status and soil data or error message.
    """
    # SoilGrids v2.0 API endpoint with comprehensive soil properties
    base_url = "https://rest.isric.org/soilgrids/v2.0/properties/query"

    # Define soil properties to fetch
    properties = [
        "bdod",  # Bulk density
        "cec",  # Cation exchange capacity
        "cfvo",  # Coarse fragments
        "clay",  # Clay content
        "nitrogen",  # Nitrogen content
        "ocd",  # Organic carbon density
        "ocs",  # Organic carbon stock
        "phh2o",  # pH in water
        "sand",  # Sand content
        "silt",  # Silt content
        "soc",  # Soil organic carbon
        "wv0010",  # Water content at 10 kPa
        "wv0033",  # Water content at 33 kPa
        "wv1500",  # Water content at 1500 kPa
    ]

    # Define depth intervals
    depths = [
        "0-5cm",
        "0-30cm",
        "5-15cm",
        "15-30cm",
        "30-60cm",
        "60-100cm",
        "100-200cm",
    ]

    # Define statistical values to retrieve
    values = ["Q0.05", "Q0.5", "Q0.95", "mean", "uncertainty"]

    # Build query parameters
    params = {
        "lon": lon,
        "lat": lat,
    }

    # Add multiple property parameters
    for prop in properties:
        params[f"property"] = prop

    # Add multiple depth parameters
    for depth in depths:
        params[f"depth"] = depth

    # Add multiple value parameters
    for value in values:
        params[f"value"] = value

    try:
        # Make request with all parameters
        url = f"{base_url}?lon={lon}&lat={lat}"
        for prop in properties:
            url += f"&property={prop}"
        for depth in depths:
            url += f"&depth={depth}"
        for value in values:
            url += f"&value={value}"

        response = requests.get(url, timeout=100, headers={"accept": "application/json"})
        response.raise_for_status()

        soil_data = response.json()

        # Parse the v2.0 API response structure
        processed_data = {}

        if "properties" in soil_data:
            for prop_name, prop_data in soil_data["properties"].items():
                processed_data[prop_name] = {}

                # Extract data for each depth layer
                for layer in prop_data.get("layers", []):
                    depth_label = layer.get("name", "unknown")
                    layer_values = {}

                    # Extract statistical values
                    for stat_name, stat_value in layer.get("values", {}).items():
                        layer_values[stat_name] = stat_value

                    processed_data[prop_name][depth_label] = layer_values

        return {
            "status": "success",
            "latitude": lat,
            "longitude": lon,
            "api_version": "v2.0",
            "soil_properties": processed_data,
            "raw_response": soil_data,
            "summary": {
                "properties_count": len(processed_data),
                "depth_layers": depths,
                "statistical_values": values,
            },
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to fetch SoilGrids v2.0 data: {str(e)}",
        }


root_agent = Agent(
    name="multi_api_streaming_agent",
    model="gemini-2.5-flash-live-preview",
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
    tools=[google_search, get_current_weather, get_soilgrids_data],
)
