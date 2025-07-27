"""
Search MCP Tools

Provides government schemes search and agricultural research capabilities
through the MCP interface. Integrates with existing NammaKrushi search services.
"""

import logging
from typing import Dict, Any, List
from ..tools.scheme_search import search_government_schemes
from ..tools.exa_search import exa_search_agricultural
from ..tools.search import google_search
from ..security.zero_retention import get_zero_retention_proxy

logger = logging.getLogger(__name__)


class GovernmentSchemesTool:
    """
    MCP tool for searching government agricultural schemes and subsidies.

    Provides access to government programs, subsidies, and financial assistance
    while maintaining zero data retention.
    """

    def __init__(self):
        self.zero_retention_proxy = get_zero_retention_proxy()

    async def search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for government agricultural schemes and subsidies.

        Args:
            args: Sanitized arguments containing:
                - query: Search query for schemes
                - state: State name (optional, defaults to Karnataka)
                - max_results: Maximum results to return (optional)

        Returns:
            Government schemes search results with detailed information
        """
        try:
            # Extract and validate parameters
            query = args.get("query", "").strip()
            state = args.get("state", "Karnataka").strip()
            max_results = args.get("max_results", 10)

            if not query:
                return {
                    "error": "missing_query",
                    "message": "Search query is required for government schemes search",
                }

            # Validate max_results
            if not isinstance(max_results, int) or max_results < 1 or max_results > 50:
                max_results = 10

            # Perform government schemes search
            search_results = await search_government_schemes(query, max_results)

            if not search_results or search_results.get("status") != "success":
                return {
                    "error": "search_failed",
                    "message": "Unable to search government schemes. Please try again.",
                }

            # Format results for MCP consumption
            formatted_result = self._format_schemes_results(
                search_results, query, state
            )

            logger.info(f"Government schemes search completed for query: {query}")
            return formatted_result

        except Exception as e:
            logger.error(f"Error in government schemes search: {e}")
            return {
                "error": "schemes_search_failed",
                "message": "Unable to complete government schemes search. Please try again.",
                "details": str(e) if logger.isEnabledFor(logging.DEBUG) else None,
            }

    def _format_schemes_results(
        self, search_results: Dict[str, Any], query: str, state: str
    ) -> Dict[str, Any]:
        """
        Format government schemes search results for MCP consumption.

        Args:
            search_results: Raw search results from schemes service
            query: Original search query
            state: State name

        Returns:
            Formatted schemes results with structured information
        """
        try:
            schemes = search_results.get("schemes", [])

            formatted_schemes = []
            for scheme in schemes:
                formatted_scheme = {
                    "scheme_name": scheme.get("name", "Unknown Scheme"),
                    "description": scheme.get("description", ""),
                    "eligibility": scheme.get("eligibility", []),
                    "benefits": scheme.get("benefits", []),
                    "application_process": scheme.get("application_process", ""),
                    "required_documents": scheme.get("documents", []),
                    "contact_information": scheme.get("contact", {}),
                    "deadline": scheme.get("deadline", ""),
                    "scheme_type": scheme.get("type", ""),
                    "target_beneficiaries": scheme.get("target_group", []),
                    "funding_amount": scheme.get("funding", ""),
                    "implementing_agency": scheme.get("agency", ""),
                }
                formatted_schemes.append(formatted_scheme)

            # Generate summary and recommendations
            summary = self._generate_schemes_summary(formatted_schemes, query)

            formatted_result = {
                "status": "success",
                "search_query": query,
                "state": state,
                "total_schemes_found": len(formatted_schemes),
                "search_summary": summary,
                "schemes": formatted_schemes,
                "application_tips": self._get_application_tips(),
                "additional_resources": self._get_additional_resources(state),
            }

            return formatted_result

        except Exception as e:
            logger.error(f"Error formatting schemes results: {e}")
            return {
                "error": "formatting_failed",
                "message": "Search completed but result formatting failed",
                "raw_results": search_results,
            }

    def _generate_schemes_summary(
        self, schemes: List[Dict[str, Any]], query: str
    ) -> str:
        """Generate a summary of found schemes."""
        if not schemes:
            return (
                f"No government schemes found for '{query}'. Try broader search terms."
            )

        scheme_types = set()
        total_schemes = len(schemes)

        for scheme in schemes:
            scheme_type = scheme.get("scheme_type", "General")
            if scheme_type:
                scheme_types.add(scheme_type)

        summary = f"Found {total_schemes} government scheme(s) related to '{query}'. "

        if scheme_types:
            types_list = ", ".join(sorted(scheme_types))
            summary += f"Scheme categories include: {types_list}. "

        summary += "Review eligibility criteria and application deadlines carefully."

        return summary

    def _get_application_tips(self) -> List[str]:
        """Get general tips for applying to government schemes."""
        return [
            "Verify eligibility criteria before applying",
            "Prepare all required documents in advance",
            "Apply before the deadline to avoid rejection",
            "Keep copies of all submitted documents",
            "Follow up on application status regularly",
            "Contact implementing agency for clarifications",
            "Ensure all information provided is accurate and complete",
        ]

    def _get_additional_resources(self, state: str) -> Dict[str, str]:
        """Get additional resources for government schemes."""
        resources = {
            "national_portal": "https://www.india.gov.in/",
            "agriculture_ministry": "https://agricoop.nic.in/",
            "pm_kisan": "https://pmkisan.gov.in/",
            "soil_health_card": "https://soilhealth.dac.gov.in/",
        }

        if state.lower() == "karnataka":
            resources.update(
                {
                    "karnataka_agriculture": "https://raitamitra.kar.nic.in/",
                    "karnataka_schemes": "https://www.karnataka.gov.in/",
                    "bhoomi_portal": "https://landrecords.karnataka.gov.in/",
                }
            )

        return resources


class AgriculturalResearchTool:
    """
    MCP tool for searching agricultural research and best practices.

    Provides access to scientific literature, research findings, and
    agricultural best practices while maintaining zero data retention.
    """

    def __init__(self):
        self.zero_retention_proxy = get_zero_retention_proxy()

    async def search(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search agricultural research and best practices.

        Args:
            args: Sanitized arguments containing:
                - query: Research query
                - search_type: Type of search (general, agricultural, scientific)

        Returns:
            Agricultural research search results
        """
        try:
            # Extract and validate parameters
            query = args.get("query", "").strip()
            search_type = args.get("search_type", "agricultural").strip().lower()

            if not query:
                return {
                    "error": "missing_query",
                    "message": "Search query is required for agricultural research search",
                }

            # Validate search type
            valid_types = ["general", "agricultural", "scientific"]
            if search_type not in valid_types:
                search_type = "agricultural"

            # Perform appropriate search based on type
            if search_type == "agricultural":
                search_results = exa_search_agricultural(query)
            elif search_type == "general":
                search_results = await google_search(query)
            else:  # scientific
                # Use Exa search with scientific focus
                search_results = exa_search_agricultural(f"scientific research {query}")

            if not search_results or search_results.get("status") != "success":
                return {
                    "error": "research_search_failed",
                    "message": "Unable to search agricultural research. Please try again.",
                }

            # Format results for MCP consumption
            formatted_result = self._format_research_results(
                search_results, query, search_type
            )

            logger.info(f"Agricultural research search completed for query: {query}")
            return formatted_result

        except Exception as e:
            logger.error(f"Error in agricultural research search: {e}")
            return {
                "error": "research_search_failed",
                "message": "Unable to complete agricultural research search. Please try again.",
                "details": str(e) if logger.isEnabledFor(logging.DEBUG) else None,
            }

    def _format_research_results(
        self, search_results: Dict[str, Any], query: str, search_type: str
    ) -> Dict[str, Any]:
        """
        Format agricultural research search results for MCP consumption.

        Args:
            search_results: Raw search results from research service
            query: Original search query
            search_type: Type of search performed

        Returns:
            Formatted research results with structured information
        """
        try:
            results = search_results.get("results", [])

            formatted_results = []
            for result in results:
                formatted_result = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "summary": result.get("text", result.get("snippet", "")),
                    "highlights": result.get("highlights", []),
                    "source": result.get("source", ""),
                    "published_date": result.get("published_date", ""),
                    "relevance_score": result.get("score", 0),
                    "content_type": self._classify_content_type(result),
                }
                formatted_results.append(formatted_result)

            # Generate research insights
            insights = self._generate_research_insights(formatted_results, query)

            formatted_response = {
                "status": "success",
                "search_query": query,
                "search_type": search_type,
                "total_results": len(formatted_results),
                "research_insights": insights,
                "results": formatted_results,
                "search_recommendations": self._get_search_recommendations(
                    query, search_type
                ),
                "related_topics": self._extract_related_topics(formatted_results),
            }

            return formatted_response

        except Exception as e:
            logger.error(f"Error formatting research results: {e}")
            return {
                "error": "formatting_failed",
                "message": "Research search completed but result formatting failed",
                "raw_results": search_results,
            }

    def _classify_content_type(self, result: Dict[str, Any]) -> str:
        """Classify the type of research content."""
        url = result.get("url", "").lower()
        title = result.get("title", "").lower()

        if any(
            domain in url
            for domain in ["researchgate.net", "sciencedirect.com", "springer.com"]
        ):
            return "Scientific Paper"
        elif any(
            domain in url
            for domain in ["extension.org", "icar.org.in", "agricoop.nic.in"]
        ):
            return "Extension Publication"
        elif "blog" in url or "news" in url:
            return "News/Blog"
        elif any(keyword in title for keyword in ["study", "research", "analysis"]):
            return "Research Study"
        else:
            return "General Information"

    def _generate_research_insights(
        self, results: List[Dict[str, Any]], query: str
    ) -> Dict[str, Any]:
        """Generate insights from research results."""
        insights = {
            "key_findings": [],
            "research_trends": [],
            "practical_applications": [],
            "knowledge_gaps": [],
        }

        # Extract key findings from highlights and summaries
        for result in results[:5]:  # Focus on top 5 results
            highlights = result.get("highlights", [])
            summary = result.get("summary", "")

            # Extract key findings from highlights
            for highlight in highlights[:2]:  # Top 2 highlights per result
                if len(highlight) > 50:  # Meaningful highlights
                    insights["key_findings"].append(
                        {"finding": highlight, "source": result.get("title", "Unknown")}
                    )

        # Identify research trends
        content_types = {}
        for result in results:
            content_type = result.get("content_type", "General")
            content_types[content_type] = content_types.get(content_type, 0) + 1

        if content_types:
            most_common = max(content_types, key=content_types.get)
            insights["research_trends"].append(
                f"Most research content is from {most_common} sources"
            )

        # Generate practical applications
        insights["practical_applications"] = [
            "Review research findings for applicability to your specific conditions",
            "Consider pilot testing recommended practices on small areas first",
            "Consult with local agricultural experts before implementing new techniques",
            "Monitor and document results for future reference",
        ]

        # Identify potential knowledge gaps
        if len(results) < 5:
            insights["knowledge_gaps"].append(
                "Limited research available on this specific topic"
            )

        return insights

    def _get_search_recommendations(self, query: str, search_type: str) -> List[str]:
        """Get recommendations for improving search results."""
        recommendations = []

        if search_type == "general":
            recommendations.append(
                "Try 'agricultural' search type for more specialized results"
            )

        if len(query.split()) < 3:
            recommendations.append("Use more specific search terms for better results")

        recommendations.extend(
            [
                "Include location-specific terms for regional relevance",
                "Add crop names or farming practices for targeted results",
                "Use scientific terms for research-focused searches",
                "Try different keyword combinations if results are limited",
            ]
        )

        return recommendations

    def _extract_related_topics(self, results: List[Dict[str, Any]]) -> List[str]:
        """Extract related topics from search results."""
        related_topics = set()

        # Extract topics from titles and highlights
        for result in results[:10]:  # Top 10 results
            title = result.get("title", "").lower()
            highlights = result.get("highlights", [])

            # Simple keyword extraction (could be enhanced with NLP)
            keywords = [
                "sustainable",
                "organic",
                "precision",
                "irrigation",
                "fertilizer",
                "pest",
                "disease",
                "yield",
                "soil",
                "climate",
                "technology",
            ]

            for keyword in keywords:
                if keyword in title or any(keyword in h.lower() for h in highlights):
                    related_topics.add(keyword.title())

        return list(related_topics)[:10]  # Limit to 10 related topics
