import sys
import traceback

import uvicorn
from mcp.server.fastmcp import FastMCP, Context
from starlette.applications import Starlette
from starlette.routing import Mount

from brave_mcp_langchain.helper import searcher, fetcher


mcp = FastMCP("brave-search")


@mcp.tool()
async def search(query: str, ctx: Context, max_results: int = 10) -> str:
    """
    Search Brave and return formatted results.

    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 10)
        ctx: MCP context for logging
    """
    try:
        results = await searcher.search(query, max_results)
        return searcher.format_results_for_llm(results)
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return f"An error occurred while searching: {str(e)}"


@mcp.tool()
async def fetch_content(url: str, ctx: Context) -> str:
    """
    Fetch and parse content from a webpage URL.

    Args:
        url: The webpage URL to fetch content from
        ctx: MCP context for logging
    """
    return await fetcher.fetch_and_parse(url)


def main():
    port = 5000

    if len(sys.argv) > 1 and sys.argv[1].lower() == "sse":
        if len(sys.argv) == 3:
            try:
                port = int(sys.argv[2])
            except ValueError:
                logger.info(f'Wrong port {sys.argv[2]} was provided. It will use default port 5000')
        else:
            logger.info(f'It will use default port 5000')

        app = Starlette(
            routes=[
                Mount('/', app=mcp.sse_app()),
            ]
        )
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        mcp.run()
