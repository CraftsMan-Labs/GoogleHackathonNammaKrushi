"""
Google Search Tool for Agricultural Assistant

Provides Google Custom Search functionality for agricultural research and information.
"""

import os
import logging
import requests
from typing import Dict, Any


async def google_search(query: str) -> Dict[str, Any]:
    """
    Performs a Google search and returns a list of results.

    Args:
        query (str): The search query string

    Returns:
        Dict[str, Any]: Search results with status and formatted results
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": os.getenv("GOOGLE_SEARCH_API_KEY"),
        "cx": os.getenv("GOOGLE_SEARCH_CSE_ID"),
        "num": 10,
    }

    try:
        logging.info(f"Performing Google search with query: {query}")
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
        logging.error(f"Google search failed: {str(e)}")
        return {"status": "error", "error_message": f"Google search failed: {str(e)}"}


# Tool declaration for Gemini AI
SEARCH_TOOL_DECLARATION = {
    "name": "google_search",
    "description": "Performs a Google search and returns relevant results for agricultural research",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query string for agricultural information",
            }
        },
        "required": ["query"],
    },
}
