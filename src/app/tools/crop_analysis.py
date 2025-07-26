"""
Crop Analysis Tool for Agricultural Assistant

Provides crop disease identification using Google Vision API and enhanced search.
"""

import os
import logging
import requests
from typing import Dict, Any


async def analyze_crop_image_and_search(
    image_input: str, farmer_query: str, include_visual_search: bool = True
) -> Dict[str, Any]:
    """
    Analyzes a diseased crop image using Google Vision API and performs a web search.

    Args:
        image_input (str): Base64 encoded image data
        farmer_query (str): Farmer's description or question about the crop disease
        include_visual_search (bool): Whether to include visual search

    Returns:
        Dict[str, Any]: Analysis results with image analysis and search results
    """
    try:
        # Clean base64 image data
        image_base64 = image_input.replace("data:image/jpeg;base64,", "").replace(
            "data:image/png;base64,", ""
        )
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Failed to process image: {str(e)}",
        }

    # Analyze image with Google Vision API
    vision_analysis = {}
    try:
        vision_api_key = os.getenv("GOOGLE_VISION_API_KEY")
        if not vision_api_key:
            vision_analysis = {"error": "Google Vision API key not configured"}
        else:
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

            response = requests.post(
                f"{vision_url}?key={vision_api_key}", json=vision_request
            )
            response.raise_for_status()
            vision_data = response.json()

            if "responses" in vision_data and vision_data["responses"]:
                response = vision_data["responses"][0]

                labels = []
                if "labelAnnotations" in response:
                    labels = [
                        label["description"]
                        for label in response["labelAnnotations"][:5]
                    ]

                web_entities = []
                if (
                    "webDetection" in response
                    and "webEntities" in response["webDetection"]
                ):
                    web_entities = [
                        entity.get("description", "")
                        for entity in response["webDetection"]["webEntities"]
                        if entity.get("description")
                    ][:3]

                vision_analysis = {
                    "labels": labels,
                    "web_entities": web_entities,
                }

    except Exception as e:
        logging.error(f"Vision API error: {str(e)}")
        vision_analysis = {"error": f"Vision API failed: {str(e)}"}

    # Enhanced search based on image analysis
    search_terms = []
    if vision_analysis.get("web_entities"):
        search_terms.extend(vision_analysis["web_entities"][:2])

    # Crop disease keywords for filtering relevant labels
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
        "rot",
        "mold",
        "insect",
    ]

    if vision_analysis.get("labels"):
        relevant_labels = [
            label
            for label in vision_analysis["labels"]
            if any(keyword in label.lower() for keyword in crop_disease_keywords)
        ]
        search_terms.extend(relevant_labels[:2])

    search_terms.append(farmer_query)
    enhanced_query = (
        " ".join(search_terms) if search_terms[:-1] else f"crop disease {farmer_query}"
    )

    # Perform enhanced search (will be handled by registry)
    search_results = {"status": "pending", "query": enhanced_query}

    return {
        "status": "success",
        "farmer_query": farmer_query,
        "image_analysis": vision_analysis,
        "search_results": search_results,
        "enhanced_query": enhanced_query,
    }


# Tool declaration for Gemini AI
CROP_ANALYSIS_TOOL_DECLARATION = {
    "name": "analyze_crop_image_and_search",
    "description": "Analyzes a crop disease image and performs enhanced search for treatment recommendations",
    "parameters": {
        "type": "object",
        "properties": {
            "image_input": {
                "type": "string",
                "description": "Base64 encoded image data of the crop",
            },
            "farmer_query": {
                "type": "string",
                "description": "Farmer's description or question about the crop disease",
            },
            "include_visual_search": {
                "type": "boolean",
                "description": "Whether to include visual search",
                "default": True,
            },
        },
        "required": ["image_input", "farmer_query"],
    },
}
