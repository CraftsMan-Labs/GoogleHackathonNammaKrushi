"""
Exa Search Tool for Agricultural Assistant

Provides Exa AI-powered search functionality for enhanced agricultural research and information.
"""

import logging
from typing import Dict, Any, Optional, List
from exa_py import Exa
from app.config.settings import settings


def exa_search(
    query: str,
    num_results: int = 10,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
    start_crawl_date: Optional[str] = None,
    end_crawl_date: Optional[str] = None,
    start_published_date: Optional[str] = None,
    end_published_date: Optional[str] = None,
    use_autoprompt: bool = True,
    type_filter: str = "neural",
    category: str = "research paper",
    include_text: bool = True,
    include_highlights: bool = True,
    text_length_limit: int = 1000,
) -> Dict[str, Any]:
    """
    Performs an Exa search and returns enhanced search results with content.

    Args:
        query (str): The search query string
        num_results (int): Number of results to return (default: 10, max: 100)
        include_domains (List[str], optional): Domains to include in search
        exclude_domains (List[str], optional): Domains to exclude from search
        start_crawl_date (str, optional): Start date for crawl filter (YYYY-MM-DD)
        end_crawl_date (str, optional): End date for crawl filter (YYYY-MM-DD)
        start_published_date (str, optional): Start date for published filter (YYYY-MM-DD)
        end_published_date (str, optional): End date for published filter (YYYY-MM-DD)
        use_autoprompt (bool): Whether to use Exa's autoprompt feature
        type_filter (str): Type of search ("neural" or "keyword")
        category (str): Content category filter
        include_text (bool): Whether to include full text content
        include_highlights (bool): Whether to include highlights
        text_length_limit (int): Maximum text length per result

    Returns:
        Dict[str, Any]: Search results with status and formatted results
    """
    exa_api_key = settings.EXA_API_KEY
    if not exa_api_key:
        return {
            "status": "error",
            "error_message": "EXA_API_KEY not found in environment variables",
        }

    try:
        logging.info(f"Performing Exa search with query: {query}")

        # Initialize Exa client
        exa = Exa(api_key=exa_api_key)

        # Perform search with content
        search_response = exa.search_and_contents(
            query=query,
            num_results=min(num_results, 100),
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            start_crawl_date=start_crawl_date,
            end_crawl_date=end_crawl_date,
            start_published_date=start_published_date,
            end_published_date=end_published_date,
            use_autoprompt=use_autoprompt,
            type=type_filter,
            category=category,
            text=include_text,
            highlights=include_highlights,
        )

        results = search_response.results

        if not results:
            return {"status": "success", "results": "No results found."}

        # Format results for better readability
        search_results = []
        for item in results:
            result_item = {
                "title": item.title or "No title",
                "url": item.url or "",
                "id": item.id or "",
                "score": item.score or 0,
                "published_date": item.published_date or "Unknown",
                "author": item.author or "Unknown",
            }

            # Add text content if available
            if include_text and hasattr(item, "text") and item.text:
                text_content = item.text
                if len(text_content) > text_length_limit:
                    text_content = text_content[:text_length_limit] + "..."
                result_item["text"] = text_content

            # Add highlights if available
            if include_highlights and hasattr(item, "highlights") and item.highlights:
                result_item["highlights"] = item.highlights

            search_results.append(result_item)

        # Format results for display
        formatted_results = []
        for i, item in enumerate(search_results):
            result_text = f"{i + 1}. **{item['title']}**\n"
            result_text += f"   URL: {item['url']}\n"
            result_text += f"   Score: {item['score']:.3f}\n"
            result_text += f"   Published: {item['published_date']}\n"
            result_text += f"   Author: {item['author']}\n"

            if "text" in item:
                result_text += f"   Content: {item['text']}\n"

            if "highlights" in item and item["highlights"]:
                result_text += f"   Highlights: {', '.join(item['highlights'])}\n"

            formatted_results.append(result_text)

        final_results = "\n".join(formatted_results)

        return {
            "status": "success",
            "results": final_results,
            "total_results": len(search_results),
            "raw_data": search_results,
        }

    except Exception as e:
        logging.error(f"Exa search failed: {str(e)}")
        return {"status": "error", "error_message": f"Exa search failed: {str(e)}"}


def exa_search_agricultural(query: str) -> Dict[str, Any]:
    """
    Performs an Exa search specifically optimized for agricultural content.

    Args:
        query (str): The agricultural search query

    Returns:
        Dict[str, Any]: Search results optimized for agricultural information
    """
    # Agricultural-focused domains for better results
    agricultural_domains = [
        "extension.org",
        "agritech.tnau.ac.in",
        "icar.org.in",
        "fao.org",
        "usda.gov",
        "agriculture.com",
        "cropscience.bayer.com",
        "pioneer.com",
        "syngenta.com",
        "corteva.com",
        "agfundernews.com",
        "modernfarmer.com",
        "farmprogress.com",
        "agriculture.gov.in",
        "krishijagran.com",
        "agrifarming.in",
    ]

    return exa_search(
        query=query,
        num_results=8,
        include_domains=agricultural_domains,
        use_autoprompt=True,
        type_filter="neural",
        category="research paper",
        include_text=True,
        include_highlights=True,
        text_length_limit=800,
    )


# Tool declarations for Gemini AI
EXA_SEARCH_TOOL_DECLARATION = {
    "name": "exa_search",
    "description": "Performs an advanced AI-powered search using Exa API for comprehensive research with content extraction and highlights",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query string for comprehensive research",
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results to return (default: 10, max: 100)",
                "default": 10,
            },
            "include_domains": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of domains to include in search (optional)",
            },
            "exclude_domains": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of domains to exclude from search (optional)",
            },
            "use_autoprompt": {
                "type": "boolean",
                "description": "Whether to use Exa's autoprompt feature for query enhancement",
                "default": True,
            },
            "include_text": {
                "type": "boolean",
                "description": "Whether to include full text content from pages",
                "default": True,
            },
            "include_highlights": {
                "type": "boolean",
                "description": "Whether to include highlighted relevant excerpts",
                "default": True,
            },
        },
        "required": ["query"],
    },
}

EXA_AGRICULTURAL_SEARCH_TOOL_DECLARATION = {
    "name": "exa_search_agricultural",
    "description": "Performs an AI-powered search specifically optimized for agricultural content using trusted agricultural domains and sources",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The agricultural search query for farming, crops, soil, weather, or agricultural research",
            }
        },
        "required": ["query"],
    },
}
