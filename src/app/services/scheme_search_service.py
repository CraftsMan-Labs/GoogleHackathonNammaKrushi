"""
Government Scheme Search Service

Service for searching government schemes using Exa AI and converting to structured output using Gemini AI.
"""

import logging
from typing import Dict, Any, List, Optional
import google.generativeai as genai

from ..config.settings import settings
from ..tools.exa_search import exa_search
from ..schemas.scheme import GovernmentScheme, SchemeSearchResponse, SchemeSearchError


class SchemeSearchService:
    """Service for searching and structuring government scheme data."""

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required for scheme search service")

        # Configure Gemini AI
        genai.configure(api_key=settings.GEMINI_API_KEY)

        # Define the structured output schema
        self.scheme_schema = genai.protos.Schema(
            type=genai.protos.Type.OBJECT,
            properties={
                "schemes": genai.protos.Schema(
                    type=genai.protos.Type.ARRAY,
                    items=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={
                            "title": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Official title/name of the government scheme",
                            ),
                            "description": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Detailed description of the scheme, its benefits, and eligibility",
                            ),
                            "scheme_link": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Official website URL or link to the scheme details",
                                nullable=True,
                            ),
                            "department": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Government department or ministry responsible for the scheme",
                                nullable=True,
                            ),
                            "eligibility": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Key eligibility criteria for the scheme",
                                nullable=True,
                            ),
                            "benefits": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Key benefits or financial assistance provided",
                                nullable=True,
                            ),
                            "application_process": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="How to apply for the scheme",
                                nullable=True,
                            ),
                            "target_beneficiaries": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Target group or beneficiaries",
                                nullable=True,
                            ),
                            "state_or_central": genai.protos.Schema(
                                type=genai.protos.Type.STRING,
                                description="Whether it's a state or central government scheme",
                                nullable=True,
                            ),
                        },
                        required=["title", "description"],
                    ),
                )
            },
            required=["schemes"],
        )

        # Create model with structured output
        self.model = genai.GenerativeModel(
            "gemini-2.5-flash",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=self.scheme_schema,
            ),
        )

    async def search_schemes(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search for government schemes using Exa AI and structure the results using Gemini AI.

        Args:
            query (str): Search query for government schemes
            max_results (int): Maximum number of schemes to return

        Returns:
            Dict[str, Any]: Structured scheme search results
        """
        try:
            logging.info(f"Starting scheme search for query: {query}")

            # Step 1: Enhance query for government schemes
            enhanced_query = self._enhance_scheme_query(query)
            logging.info(f"Enhanced query: {enhanced_query}")

            # Step 2: Use exa_search function to get comprehensive content data
            exa_result = exa_search(
                query=enhanced_query,
                num_results=min(max_results * 2, 20),  # Get more results for filtering
                include_domains=[
                    "gov.in",
                    "nic.in",
                    "india.gov.in",
                    "karnataka.gov.in",
                    "agricoop.gov.in",
                    "pmkisan.gov.in",
                    "dbtbharat.gov.in",
                    "vikaspedia.in",
                    "farmer.gov.in",
                    "agritech.tnau.ac.in",
                    "icar.org.in",
                    "nabard.org",
                    "kisan.gov.in",
                    "pmfby.gov.in",
                    "agriculture.gov.in",
                ],
                use_autoprompt=True,
                type_filter="neural",
                include_text=True,  # Get full text content from pages
                include_highlights=True,  # Get highlighted relevant excerpts
                text_length_limit=2000,  # Increased limit for comprehensive content
            )

            if exa_result["status"] != "success":
                return {
                    "status": "error",
                    "error_message": f"Exa search failed: {exa_result.get('error_message', 'Unknown error')}",
                    "query": query,
                }

            # Step 3: Extract raw search results with full content
            raw_results = exa_result.get("raw_data", [])
            if not raw_results:
                return {
                    "status": "success",
                    "query": query,
                    "total_schemes": 0,
                    "schemes": [],
                    "search_metadata": {"exa_results": 0},
                }

            # Step 4: Use Gemini AI to structure the results
            structured_schemes = await self._structure_with_gemini(raw_results, query)

            # Step 5: Validate and format response
            response = {
                "status": "success",
                "query": query,
                "total_schemes": len(structured_schemes),
                "schemes": structured_schemes,
                "search_metadata": {
                    "exa_results": len(raw_results),
                    "structured_results": len(structured_schemes),
                    "enhanced_query": enhanced_query,
                },
            }

            logging.info(
                f"Scheme search completed: {len(structured_schemes)} schemes found"
            )
            return response

        except Exception as e:
            logging.error(f"Scheme search failed: {str(e)}")
            return {
                "status": "error",
                "error_message": f"Scheme search failed: {str(e)}",
                "query": query,
            }

    def _enhance_scheme_query(self, query: str) -> str:
        """Enhance the search query to focus on government schemes."""
        # Add scheme-specific keywords if not present
        scheme_keywords = [
            "government scheme",
            "subsidy",
            "yojana",
            "pradhan mantri",
            "ministry",
            "department",
            "central scheme",
            "state scheme",
            "agricultural scheme",
            "farmer scheme",
            "rural development",
        ]

        query_lower = query.lower()
        has_scheme_keywords = any(keyword in query_lower for keyword in scheme_keywords)

        if not has_scheme_keywords:
            enhanced_query = f"{query} government scheme subsidy yojana"
        else:
            enhanced_query = query

        # Add location context for better results
        if "karnataka" not in query_lower and "india" not in query_lower:
            enhanced_query += " Karnataka India"

        return enhanced_query

    async def _structure_with_gemini(
        self, raw_results: List[Dict], query: str
    ) -> List[Dict[str, Any]]:
        """Use Gemini AI to convert raw search results into structured scheme data."""

        # Prepare the prompt for Gemini AI
        prompt = self._create_structuring_prompt(raw_results, query)

        try:
            # Generate structured output using Gemini
            response = self.model.generate_content(prompt)

            if not response.text:
                logging.warning("Gemini returned empty response")
                return []

            # Parse the structured JSON response
            try:
                import json

                structured_data = json.loads(response.text)

                # Extract schemes from the structured response
                schemes = structured_data.get("schemes", [])

                # Validate each scheme and filter valid ones
                valid_schemes = []
                for scheme in schemes:
                    if self._validate_scheme_data(scheme):
                        valid_schemes.append(scheme)

                return valid_schemes[:10]  # Limit to 10 schemes

            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse Gemini structured response: {e}")
                logging.error(f"Raw response: {response.text[:500]}...")
                return []

        except Exception as e:
            logging.error(f"Gemini structuring failed: {str(e)}")
            return []

    def _create_structuring_prompt(self, raw_results: List[Dict], query: str) -> str:
        """Create a prompt for Gemini AI to structure the search results."""

        # Prepare the raw Exa search data for Gemini processing
        results_text = ""
        for i, result in enumerate(raw_results[:10], 1):  # Limit to 10 results
            results_text += f"\n--- Exa Search Result {i} ---\n"
            results_text += f"Title: {result.get('title', 'No title')}\n"
            results_text += f"URL: {result.get('url', 'No URL')}\n"
            results_text += f"Score: {result.get('score', 'N/A')}\n"
            results_text += (
                f"Published Date: {result.get('published_date', 'Unknown')}\n"
            )
            results_text += f"Author: {result.get('author', 'Unknown')}\n"

            # Include full text content from Exa search
            full_content = result.get("text", "No content")
            if len(full_content) > 1500:
                results_text += f"Content: {full_content[:1500]}...\n"
            else:
                results_text += f"Content: {full_content}\n"

            # Include highlights if available
            if result.get("highlights"):
                results_text += f"Highlights: {', '.join(result['highlights'][:5])}\n"

        prompt = f"""
You are an expert in Indian government schemes and agricultural policies. I have used Exa AI search to find comprehensive content about government schemes for the query "{query}". 

The Exa search has returned detailed content from official government websites including full text, highlights, and metadata. Your task is to analyze this rich content and extract structured information about government schemes.

EXA SEARCH RESULTS WITH FULL CONTENT:
{results_text}

TASK: Convert the above Exa search results into structured information about government schemes. Extract information from the full content provided.

INSTRUCTIONS:
1. Only extract information about actual government schemes, subsidies, or programs
2. Ignore general articles, news, or non-scheme content
3. Ensure descriptions are informative and accurate (50-500 words)
4. Use official scheme names as titles
5. Include financial benefits/amounts when mentioned
6. Focus on schemes relevant to agriculture, farming, or rural development when possible
7. For each scheme, provide:
   - title: Official scheme name (required)
   - description: Detailed description of the scheme (required)
   - scheme_link: Official URL if available
   - department: Government department/ministry
   - eligibility: Key eligibility criteria
   - benefits: Key benefits or financial assistance
   - application_process: How to apply
   - target_beneficiaries: Target group
   - state_or_central: "Central" or "State" or "Both"

Extract and structure the government schemes from the search results:
"""
        return prompt

    def _validate_scheme_data(self, scheme: Dict[str, Any]) -> bool:
        """Validate that a scheme has the required fields and reasonable data."""

        # Check required fields
        if not isinstance(scheme, dict):
            return False

        title = scheme.get("title", "").strip()
        description = scheme.get("description", "").strip()

        # Validate required fields
        if not title or len(title) < 5:
            return False

        if not description or len(description) < 20:
            return False

        # Check for reasonable content (not just generic text)
        scheme_indicators = [
            "scheme",
            "yojana",
            "subsidy",
            "program",
            "programme",
            "ministry",
            "department",
            "government",
            "benefit",
            "assistance",
            "support",
            "fund",
            "grant",
        ]

        combined_text = (title + " " + description).lower()
        has_scheme_indicators = any(
            indicator in combined_text for indicator in scheme_indicators
        )

        return has_scheme_indicators

    def get_scheme_search_info(self) -> Dict[str, Any]:
        """Get information about the scheme search service."""
        return {
            "service": "Government Scheme Search",
            "description": "Search for government schemes using Exa AI and structure results with Gemini AI",
            "features": [
                "Exa AI-powered search with government domains",
                "Gemini AI structured output conversion",
                "Focus on agricultural and rural schemes",
                "Comprehensive scheme information extraction",
            ],
            "supported_queries": [
                "Agricultural subsidies for farmers",
                "PM-KISAN scheme details",
                "Karnataka government farming schemes",
                "Crop insurance schemes",
                "Rural development programs",
            ],
            "output_fields": [
                "title",
                "description",
                "scheme_link",
                "department",
                "eligibility",
                "benefits",
                "application_process",
                "target_beneficiaries",
                "state_or_central",
            ],
        }


# Global service instance
_scheme_search_service = None


def get_scheme_search_service() -> SchemeSearchService:
    """Get or create the global scheme search service instance."""
    global _scheme_search_service
    if _scheme_search_service is None:
        _scheme_search_service = SchemeSearchService()
    return _scheme_search_service
