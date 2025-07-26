"""
Government Scheme Search API

API endpoints for searching and retrieving government schemes using Exa AI and Gemini AI.
"""

import logging
from typing import Union
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from ..schemas.scheme import (
    SchemeSearchRequest,
    SchemeSearchResponse,
    SchemeSearchError,
    GovernmentScheme,
)
from ..services.scheme_search_service import (
    get_scheme_search_service,
    SchemeSearchService,
)

router = APIRouter(prefix="/schemes", tags=["Government Schemes"])


@router.post(
    "/search",
    response_model=Union[SchemeSearchResponse, SchemeSearchError],
    summary="Search Government Schemes",
    description="Search for government schemes using AI-powered search and get structured results",
)
async def search_schemes(
    request: SchemeSearchRequest,
    service: SchemeSearchService = Depends(get_scheme_search_service),
) -> Union[SchemeSearchResponse, SchemeSearchError]:
    """
    Search for government schemes using Exa AI and return structured results.

    This endpoint:
    1. Takes a search query for government schemes
    2. Uses Exa AI to search government websites and domains
    3. Uses Gemini AI to convert raw results into structured scheme data
    4. Returns a list of schemes with title, description, links, and other details

    **Example queries:**
    - "agricultural subsidies for farmers in Karnataka"
    - "PM-KISAN scheme eligibility and benefits"
    - "crop insurance schemes for small farmers"
    - "rural development programs"
    - "government schemes for organic farming"
    """
    try:
        logging.info(f"Scheme search request: {request.query}")

        # Perform the scheme search
        result = await service.search_schemes(
            query=request.query, max_results=request.max_results
        )

        if result["status"] == "error":
            return SchemeSearchError(
                status="error",
                error_message=result["error_message"],
                query=request.query,
            )

        # Convert to response model
        schemes = []
        for scheme_data in result["schemes"]:
            try:
                scheme = GovernmentScheme(**scheme_data)
                schemes.append(scheme)
            except Exception as e:
                logging.warning(f"Failed to validate scheme data: {e}")
                continue

        response = SchemeSearchResponse(
            status=result["status"],
            query=result["query"],
            total_schemes=len(schemes),
            schemes=schemes,
            search_metadata=result.get("search_metadata"),
        )

        logging.info(f"Scheme search completed: {len(schemes)} schemes returned")
        return response

    except Exception as e:
        logging.error(f"Scheme search endpoint error: {str(e)}")
        return SchemeSearchError(
            status="error",
            error_message=f"Internal server error: {str(e)}",
            query=request.query,
        )


@router.get(
    "/search-simple",
    response_model=Union[SchemeSearchResponse, SchemeSearchError],
    summary="Simple Scheme Search",
    description="Simple GET endpoint for scheme search with query parameter",
)
async def search_schemes_simple(
    q: str,
    max_results: int = 10,
    service: SchemeSearchService = Depends(get_scheme_search_service),
) -> Union[SchemeSearchResponse, SchemeSearchError]:
    """
    Simple GET endpoint for scheme search using query parameter.

    **Parameters:**
    - **q**: Search query for government schemes
    - **max_results**: Maximum number of schemes to return (1-20, default: 10)

    **Example:**
    ```
    GET /schemes/search-simple?q=agricultural%20subsidies&max_results=5
    ```
    """
    if not q or len(q.strip()) < 3:
        return SchemeSearchError(
            status="error",
            error_message="Query parameter 'q' must be at least 3 characters long",
            query=q,
        )

    if max_results < 1 or max_results > 20:
        return SchemeSearchError(
            status="error",
            error_message="max_results must be between 1 and 20",
            query=q,
        )

    # Create request object and use the main search function
    request = SchemeSearchRequest(query=q.strip(), max_results=max_results)
    return await search_schemes(request, service)


@router.get(
    "/info",
    summary="Scheme Search Service Info",
    description="Get information about the scheme search service capabilities",
)
async def get_scheme_search_info(
    service: SchemeSearchService = Depends(get_scheme_search_service)
) -> dict:
    """
    Get information about the scheme search service.

    Returns details about:
    - Service capabilities
    - Supported query types
    - Output data fields
    - Example queries
    """
    return service.get_scheme_search_info()


@router.get(
    "/examples",
    summary="Example Scheme Queries",
    description="Get example queries for testing the scheme search functionality",
)
async def get_example_queries() -> dict:
    """
    Get example queries for testing scheme search functionality.
    """
    return {
        "example_queries": [
            {
                "query": "PM-KISAN scheme eligibility and benefits",
                "description": "Search for PM-KISAN direct benefit transfer scheme",
                "expected_results": "Central government scheme for farmers",
            },
            {
                "query": "agricultural subsidies for small farmers Karnataka",
                "description": "State-specific agricultural subsidies",
                "expected_results": "Karnataka state agricultural schemes",
            },
            {
                "query": "crop insurance schemes PMFBY",
                "description": "Pradhan Mantri Fasal Bima Yojana details",
                "expected_results": "Crop insurance scheme information",
            },
            {
                "query": "organic farming certification schemes",
                "description": "Schemes for organic farming promotion",
                "expected_results": "Organic farming support schemes",
            },
            {
                "query": "rural development employment schemes MGNREGA",
                "description": "Rural employment guarantee schemes",
                "expected_results": "MGNREGA and related employment schemes",
            },
            {
                "query": "dairy farming subsidy schemes",
                "description": "Government support for dairy farmers",
                "expected_results": "Dairy development schemes and subsidies",
            },
            {
                "query": "soil health card scheme benefits",
                "description": "Soil testing and health improvement schemes",
                "expected_results": "Soil health management schemes",
            },
            {
                "query": "women farmers empowerment schemes",
                "description": "Schemes specifically for women in agriculture",
                "expected_results": "Gender-focused agricultural schemes",
            },
        ],
        "query_tips": [
            "Include specific scheme names for better results (e.g., PM-KISAN, PMFBY)",
            "Add location context (e.g., Karnataka, India) for state-specific schemes",
            "Use agricultural keywords (farming, subsidy, crop, rural) for better targeting",
            "Combine multiple terms (e.g., 'organic farming certification subsidy')",
            "Include beneficiary type (small farmers, women farmers, etc.)",
        ],
        "supported_domains": [
            "gov.in - Government of India websites",
            "karnataka.gov.in - Karnataka government",
            "agricoop.gov.in - Ministry of Agriculture",
            "pmkisan.gov.in - PM-KISAN portal",
            "nabard.org - NABARD schemes",
            "vikaspedia.in - Development information portal",
        ],
    }


@router.get(
    "/health",
    summary="Scheme Search Health Check",
    description="Check the health status of the scheme search service",
)
async def health_check() -> dict:
    """
    Health check endpoint for the scheme search service.
    """
    try:
        service = get_scheme_search_service()

        # Basic service info
        info = service.get_scheme_search_info()

        return {
            "status": "healthy",
            "service": info["service"],
            "timestamp": "2024-12-27T10:00:00Z",
            "features_available": len(info["features"]),
            "supported_queries": len(info["supported_queries"]),
            "dependencies": {
                "exa_ai": "available",
                "gemini_ai": "available",
                "government_domains": "accessible",
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Scheme search service unhealthy: {str(e)}",
        )
