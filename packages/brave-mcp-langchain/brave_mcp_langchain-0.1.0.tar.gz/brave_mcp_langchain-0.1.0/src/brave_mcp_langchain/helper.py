from dataclasses import dataclass
import logging
import urllib.parse
import sys
import traceback
import asyncio
from datetime import datetime, timedelta
import time
import re

import httpx
from bs4 import BeautifulSoup
from typing import List


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass
class SearchResult:
    title: str
    link: str
    snippet: str
    position: int


class BrowserUserAgent:
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    )


class RateLimiter:
    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.requests = []

    async def acquire(self):
        now = datetime.now()
        # Remove requests older than 1 minute
        self.requests = [
            req for req in self.requests if now - req < timedelta(minutes=1)
        ]

        if len(self.requests) >= self.requests_per_minute:
            # Wait until we can make another request
            wait_time = 60 - (now - self.requests[0]).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)

        self.requests.append(now)


class BraveSearcher:
    BASE_URL = "https://search.brave.com/search?q={}&source=desktop"
    HEADERS = {
        "Host": "search.brave.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": BrowserUserAgent.USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate"
    }

    def __init__(self):
        self.rate_limiter = RateLimiter()

    def format_results_for_llm(self, results: List[SearchResult]) -> str:
        """Format results in a natural language style that's easier for LLMs to process"""
        if not results:
            return "No results were found for your search query. This could be due to Brave's bot detection or the query returned no matches. Please try rephrasing your search or try again in a few minutes."

        output = []
        output.append(f"Found {len(results)} search results:\n")

        for result in results:
            output.append(f"{result.position}. {result.title}")
            output.append(f"   URL: {result.link}")
            output.append(f"   Summary: {result.snippet}")
            output.append("")  # Empty line between results

        return "\n".join(output)

    async def search(
        self, query: str, max_results: int = 10
    ) -> List[SearchResult]:
        try:
            # Apply rate limiting
            await self.rate_limiter.acquire()
            logger.info(f"Searching Brave for: {query}")

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.BASE_URL.format(urllib.parse.quote_plus(query)), headers=self.HEADERS, timeout=30.0
                )
                response.raise_for_status()

            # Parse HTML response
            soup = BeautifulSoup(response.text, "html.parser")
            if not soup:
                logger.error("Failed to parse HTML response")
                return []

            results = []
            for div in soup.find_all("div", class_=lambda cls: cls and "snippet" in cls):
                a_tag = div.find("a", class_=lambda cls: cls and "heading-serpresult" in cls)
                snippet_div = div.find("div", class_=lambda cls: cls and "snippet-content" in cls)
                if a_tag:
                    title_div = a_tag.find("div", class_="title")
                    title = title_div.get_text(strip=True) if title_div else ""
                    link = a_tag.get("href", "")

                    if snippet_div:
                        snippet = snippet_div.get_text(strip=True)
                    else:
                        snippet = ""

                    results.append(
                        SearchResult(
                            title=title,
                            link=link,
                            snippet=snippet,
                            position=len(results) + 1,
                        )
                    )

                    if len(results) >= max_results:
                        break

            logger.info(f"Successfully found {len(results)} results")
            return results

        except httpx.TimeoutException:
            logger.error("Search request timed out")
            return []
        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during search: {str(e)}")
            traceback.print_exc(file=sys.stderr)
            return []


class WebContentFetcher:
    def __init__(self):
        self.rate_limiter = RateLimiter(requests_per_minute=20)

    async def fetch_and_parse(self, url: str) -> str:
        """Fetch and parse content from a webpage"""
        try:
            await self.rate_limiter.acquire()

            logger.info(f"Fetching content from: {url}")

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers={
                        "User-Agent": BrowserUserAgent.USER_AGENT
                    },
                    follow_redirects=True,
                    timeout=30.0,
                )
                response.raise_for_status()

            # Parse the HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()

            # Get the text content
            text = soup.get_text()

            # Clean up the text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = " ".join(chunk for chunk in chunks if chunk)

            # Remove extra whitespace
            text = re.sub(r"\s+", " ", text).strip()

            # Truncate if too long
            if len(text) > 8000:
                text = text[:8000] + "... [content truncated]"

            logger.info(
                f"Successfully fetched and parsed content ({len(text)} characters)"
            )
            return text

        except httpx.TimeoutException:
            logger.error(f"Request timed out for URL: {url}")
            return "Error: The request timed out while trying to fetch the webpage."
        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred while fetching {url}: {str(e)}")
            return f"Error: Could not access the webpage ({str(e)})"
        except Exception as e:
            logger.error(f"Error fetching content from {url}: {str(e)}")
            return f"Error: An unexpected error occurred while fetching the webpage ({str(e)})"


searcher = BraveSearcher()
fetcher = WebContentFetcher()
