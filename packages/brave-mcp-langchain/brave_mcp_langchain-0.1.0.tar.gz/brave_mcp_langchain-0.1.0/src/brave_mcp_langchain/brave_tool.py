from typing import Optional
import traceback
from langchain.tools import StructuredTool
from langchain_core.tools import tool
from pydantic import BaseModel
from pydantic import Field

from brave_mcp_langchain.helper import searcher, fetcher


class SearchInput(BaseModel):
    query: str = Field(description="A query to perform a web search")
    max_results: Optional[int] = Field(default=10, description="Max result limit for the search")


class FetchContentInput(BaseModel):
    url: str = Field(description="URL to get content of")


async def search(query: str, max_results: int = 10) -> str:
    """
    Search Brave and return formatted results.

    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 10)
    """
    try:
        results = await searcher.search(query, max_results)
        return searcher.format_results_for_llm(results)
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return f"An error occurred while searching: {str(e)}"


async def fetch_content(url: str) -> str:
    """
    Fetch and parse content from a webpage URL.

    Args:
        url: The webpage URL to fetch content from
    """
    return await fetcher.fetch_and_parse(url)


search_tool = StructuredTool.from_function(
    name="BraveSearch",
    description="Searches Brave and returns formatted results.",
    args_schema=SearchInput,
    coroutine=search,
    return_direct=True
)

fetch_content_tool = StructuredTool.from_function(
    name="FetchContent",
    description="Fetch and parse content from a webpage URL.",
    args_schema=FetchContentInput,  # define this using Pydantic
    coroutine=fetch_content,        # async function goes here else use func param
    return_direct=True
)


if __name__ == "__main__":
    from langchain.tools import Tool
    import httpx
    import asyncio

    async def test_search():
        result = await search_tool.ainvoke({
            "query": "LangGraph overview",
            "max_results": 10
        })
        print(result)

        result = await fetch_content_tool.ainvoke({
            "url": "https://iamatulsingh.github.io"
        })
        print(result)

    asyncio.run(test_search())
