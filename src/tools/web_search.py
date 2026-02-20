"""T028: Web search tool using Tavily API."""

from __future__ import annotations

import logging

import httpx

from src.config import settings

logger = logging.getLogger(__name__)

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


async def tavily_search(query: str, max_results: int = 10, search_depth: str = "advanced") -> list[dict]:
    """Search the web using Tavily API.

    Returns list of results with: title, url, content, relevance_score.
    """
    if not settings.tavily_api_key:
        logger.warning("TAVILY_API_KEY not set — returning empty results")
        return []

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            TAVILY_SEARCH_URL,
            json={
                "api_key": settings.tavily_api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth,
                "include_raw_content": False,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    results = []
    for item in data.get("results", []):
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "content": item.get("content", ""),
            "relevance_score": item.get("score", 0.5),
        })

    logger.info("Tavily search for '%s' returned %d results", query, len(results))
    return results
