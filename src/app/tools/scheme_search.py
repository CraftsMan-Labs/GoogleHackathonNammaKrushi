"""
Government Scheme Search Tool for Agricultural Assistant

Provides government scheme search functionality using Exa AI and Gemini AI.
"""

import logging
from typing import Dict, Any

from ..services.scheme_search_service import get_scheme_search_service


async def search_government_schemes(
    query: str, max_results: int = 10
) -> Dict[str, Any]:
    """
    Search for government schemes using AI-powered search and structured output.

    Args:
        query (str): Search query for government schemes
        max_results (int): Maximum number of schemes to return (default: 10, max: 20)

    Returns:
        Dict[str, Any]: Structured scheme search results
    """
    try:
        logging.info(f"Searching government schemes with query: {query}")

        # Validate inputs
        if not query or len(query.strip()) < 3:
            return {
                "status": "error",
                "error_message": "Query must be at least 3 characters long",
            }

        if max_results < 1 or max_results > 20:
            max_results = 10

        # Get the scheme search service
        service = get_scheme_search_service()

        # Perform the search
        result = await service.search_schemes(query.strip(), max_results)

        if result["status"] == "success":
            # Format the response for tool usage
            schemes = result.get("schemes", [])

            if not schemes:
                return {
                    "status": "success",
                    "message": f"No government schemes found for query: {query}",
                    "total_schemes": 0,
                    "schemes": [],
                }

            # Format schemes for better readability
            formatted_schemes = []
            for i, scheme in enumerate(schemes, 1):
                formatted_scheme = f"{i}. **{scheme.get('title', 'Unknown Scheme')}**\n"

                if scheme.get("department"):
                    formatted_scheme += f"   Department: {scheme['department']}\n"

                formatted_scheme += f"   Description: {scheme.get('description', 'No description available')}\n"

                if scheme.get("benefits"):
                    formatted_scheme += f"   Benefits: {scheme['benefits']}\n"

                if scheme.get("eligibility"):
                    formatted_scheme += f"   Eligibility: {scheme['eligibility']}\n"

                if scheme.get("application_process"):
                    formatted_scheme += (
                        f"   How to Apply: {scheme['application_process']}\n"
                    )

                if scheme.get("scheme_link"):
                    formatted_scheme += f"   Official Link: {scheme['scheme_link']}\n"

                if scheme.get("state_or_central"):
                    formatted_scheme += (
                        f"   Type: {scheme['state_or_central']} Government Scheme\n"
                    )

                formatted_schemes.append(formatted_scheme)

            formatted_results = "\n".join(formatted_schemes)

            return {
                "status": "success",
                "message": f"Found {len(schemes)} government schemes for: {query}",
                "total_schemes": len(schemes),
                "schemes": formatted_results,
                "raw_schemes": schemes,  # Include raw data for further processing
            }
        else:
            return {
                "status": "error",
                "error_message": result.get("error_message", "Unknown error occurred"),
            }

    except Exception as e:
        logging.error(f"Government scheme search failed: {str(e)}")
        return {"status": "error", "error_message": f"Scheme search failed: {str(e)}"}


# Tool declaration for Gemini AI
SCHEME_SEARCH_TOOL_DECLARATION = {
    "name": "search_government_schemes",
    "description": "Search for government schemes, subsidies, and programs using AI-powered search. Returns structured information about schemes including title, description, eligibility, benefits, and application process.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query for government schemes (e.g., 'agricultural subsidies for farmers', 'PM-KISAN scheme', 'crop insurance schemes')",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of schemes to return (default: 10, max: 20)",
                "default": 10,
            },
        },
        "required": ["query"],
    },
}
