"""
Soil Analysis Tool for Agricultural Assistant

Provides comprehensive soil property data using the SoilGrids v2.0 REST API.
"""

import json
import logging
import requests
from typing import Dict, Any


async def get_soilgrids_data(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetches soil property data for the given coordinates using the SoilGrids v2.0 REST API.

    Args:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate

    Returns:
        Dict[str, Any]: Soil data with status and processed soil properties
    """
    # Soil properties to fetch
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

    # Depth layers
    depths = [
        "0-5cm",
        "0-30cm",
        "5-15cm",
        "15-30cm",
        "30-60cm",
        "60-100cm",
        "100-200cm",
    ]

    # Statistical values
    values = ["Q0.05", "Q0.5", "Q0.95", "mean", "uncertainty"]

    try:
        # Build API URL
        url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}"
        for prop in properties:
            url += f"&property={prop}"
        for depth in depths:
            url += f"&depth={depth}"
        for value in values:
            url += f"&value={value}"

        # Make API request
        response = requests.get(
            url, timeout=200, headers={"accept": "application/json"}
        )
        response.raise_for_status()

        soil_data = response.json()
        processed_data = {}

        # Process the API response
        if "properties" in soil_data and "layers" in soil_data["properties"]:
            for layer in soil_data["properties"]["layers"]:
                prop_name = layer.get("name")
                if prop_name:
                    processed_data[prop_name] = {}

                    # Add unit information
                    if "unit_measure" in layer:
                        processed_data[prop_name]["unit_measure"] = layer[
                            "unit_measure"
                        ]

                    # Process depth layers
                    for depth_info in layer.get("depths", []):
                        depth_label = depth_info.get("label", "unknown")
                        depth_values = depth_info.get("values", {})
                        processed_data[prop_name][depth_label] = depth_values

        # Check if we have any valid data (not all null values)
        has_valid_data = _check_valid_data(soil_data)

        # If no valid data, use fallback values for Indian soil
        if not has_valid_data:
            processed_data = _get_fallback_soil_data(lat, lon)
            data_source = "Fallback_Indian_Soil_Data"
        else:
            data_source = "SoilGrids_v2.0"

        return {
            "status": "success",
            "data": json.dumps(processed_data),
            "coordinates": {"latitude": lat, "longitude": lon},
            "summary": _generate_soil_summary(processed_data),
            "data_source": data_source,
        }

    except Exception as e:
        logging.error(
            f"SoilGrids API request failed for coordinates {lat}, {lon}: {str(e)}"
        )
        return {
            "status": "error",
            "error_message": f"Failed to fetch SoilGrids data: {str(e)}",
        }


def _check_valid_data(soil_data: Dict[str, Any]) -> bool:
    """
    Check if the soil data contains valid (non-null) values.

    Args:
        soil_data (Dict[str, Any]): Raw soil data from SoilGrids API

    Returns:
        bool: True if valid data exists, False otherwise
    """
    try:
        if "properties" not in soil_data or "layers" not in soil_data["properties"]:
            return False

        for layer in soil_data["properties"]["layers"]:
            for depth_info in layer.get("depths", []):
                values = depth_info.get("values", {})
                if any(v is not None for v in values.values()):
                    return True
        return False
    except Exception:
        return False


def _get_fallback_soil_data(lat: float, lon: float) -> Dict[str, Any]:
    """
    Generate fallback soil data based on typical Indian soil characteristics.

    Args:
        lat (float): Latitude coordinate
        lon (float): Longitude coordinate

    Returns:
        Dict[str, Any]: Fallback soil data
    """
    # Typical Indian soil values based on region
    # These are representative values for different regions of India

    # Determine region-based soil characteristics
    if lat >= 28:  # Northern India
        base_ph = 75  # pH 7.5 (slightly alkaline)
        clay_content = 250  # 25%
        sand_content = 450  # 45%
        silt_content = 300  # 30%
        organic_carbon = 80  # 8 g/kg
    elif lat <= 15:  # Southern India
        base_ph = 65  # pH 6.5 (slightly acidic)
        clay_content = 350  # 35%
        sand_content = 350  # 35%
        silt_content = 300  # 30%
        organic_carbon = 120  # 12 g/kg
    else:  # Central India
        base_ph = 70  # pH 7.0 (neutral)
        clay_content = 300  # 30%
        sand_content = 400  # 40%
        silt_content = 300  # 30%
        organic_carbon = 100  # 10 g/kg

    return {
        "phh2o": {
            "0-30cm": {"mean": base_ph, "Q0.5": base_ph},
            "unit_measure": {
                "d_factor": 10,
                "mapped_units": "pH*10",
                "target_units": "-",
            },
        },
        "clay": {
            "0-30cm": {"mean": clay_content, "Q0.5": clay_content},
            "unit_measure": {
                "d_factor": 10,
                "mapped_units": "g/kg",
                "target_units": "%",
            },
        },
        "sand": {
            "0-30cm": {"mean": sand_content, "Q0.5": sand_content},
            "unit_measure": {
                "d_factor": 10,
                "mapped_units": "g/kg",
                "target_units": "%",
            },
        },
        "silt": {
            "0-30cm": {"mean": silt_content, "Q0.5": silt_content},
            "unit_measure": {
                "d_factor": 10,
                "mapped_units": "g/kg",
                "target_units": "%",
            },
        },
        "soc": {
            "0-30cm": {"mean": organic_carbon, "Q0.5": organic_carbon},
            "unit_measure": {
                "d_factor": 10,
                "mapped_units": "dg/kg",
                "target_units": "g/kg",
            },
        },
        "nitrogen": {
            "0-30cm": {"mean": 150, "Q0.5": 150},  # 1.5 g/kg
            "unit_measure": {
                "d_factor": 100,
                "mapped_units": "cg/kg",
                "target_units": "g/kg",
            },
        },
        "cec": {
            "0-30cm": {"mean": 180, "Q0.5": 180},  # 18 cmol(c)/kg
            "unit_measure": {
                "d_factor": 10,
                "mapped_units": "mmol(c)/kg",
                "target_units": "cmol(c)/kg",
            },
        },
        "bdod": {
            "0-30cm": {"mean": 140, "Q0.5": 140},  # 1.4 kg/dm³
            "unit_measure": {
                "d_factor": 100,
                "mapped_units": "cg/cm³",
                "target_units": "kg/dm³",
            },
        },
    }


def _generate_soil_summary(soil_data: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of soil data.

    Args:
        soil_data (Dict[str, Any]): Processed soil data

    Returns:
        str: Human-readable soil summary
    """
    summary_parts = []

    try:
        # pH analysis
        if "phh2o" in soil_data and "0-30cm" in soil_data["phh2o"]:
            ph_value = (
                soil_data["phh2o"]["0-30cm"].get("mean", 0) / 10
            )  # Convert from pH*10
            if ph_value < 6.0:
                ph_desc = "acidic"
            elif ph_value > 7.5:
                ph_desc = "alkaline"
            else:
                ph_desc = "neutral"
            summary_parts.append(f"Soil pH: {ph_value:.1f} ({ph_desc})")

        # Organic carbon
        if "soc" in soil_data and "0-30cm" in soil_data["soc"]:
            soc_value = (
                soil_data["soc"]["0-30cm"].get("mean", 0) / 10
            )  # Convert from g/kg
            if soc_value < 10:
                soc_desc = "low"
            elif soc_value > 30:
                soc_desc = "high"
            else:
                soc_desc = "moderate"
            summary_parts.append(f"Organic carbon: {soc_value:.1f} g/kg ({soc_desc})")

        # Soil texture
        texture_parts = []
        for component in ["clay", "sand", "silt"]:
            if component in soil_data and "0-30cm" in soil_data[component]:
                value = (
                    soil_data[component]["0-30cm"].get("mean", 0) / 10
                )  # Convert from %*10
                texture_parts.append(f"{component}: {value:.0f}%")

        if texture_parts:
            summary_parts.append(f"Texture - {', '.join(texture_parts)}")

        return "; ".join(summary_parts) if summary_parts else "Soil data available"

    except Exception as e:
        logging.error(f"Error generating soil summary: {str(e)}")
        return "Soil data available (summary generation failed)"


# Tool declaration for Gemini AI
SOIL_ANALYSIS_TOOL_DECLARATION = {
    "name": "get_soilgrids_data",
    "description": "Fetches comprehensive soil property data for given coordinates to help with crop planning and soil management",
    "parameters": {
        "type": "object",
        "properties": {
            "lat": {"type": "number", "description": "Latitude coordinate"},
            "lon": {"type": "number", "description": "Longitude coordinate"},
        },
        "required": ["lat", "lon"],
    },
}
