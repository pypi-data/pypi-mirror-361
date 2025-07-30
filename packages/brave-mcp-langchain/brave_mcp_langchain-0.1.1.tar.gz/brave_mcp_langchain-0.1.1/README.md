# Local test

## Create venv
```bash
uv sync
```

## Install package

```bash
uv pip install brave-mcp-langchain
```

## Run MCP server in STDIO mode

```bash
uvx brave-mcp-langchain
```

### To run MCP server in SSE mode
```bash
uvx brave-mcp-langchain sse 5003
```

## MCP Setting

```json
{
  "mcpServers": {
    "brave-mcp-langchain": {
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "uvx",
      "args": [
        "brave-mcp-langchain"
      ]
    }
  }
}
```

# Use as Langchain tool

It can also be used as Langchain tool. Try below code to try

```python
import httpx
import asyncio
from langchain.tools import Tool
from brave_mcp_langchain import brave_tool

async def test_search():
    result = await brave_tool.search_tool.ainvoke({"query": "LangGraph overview", "max_results": 10})
    print(result)

    result = await brave_tool.fetch_content_tool.ainvoke({
        "url": "https://iamatulsingh.github.io"
    })
    print(result)

asyncio.run(test_search())
```

## 🧠 Inspiration & Attribution

This project, `brave-mcp-langchain`, was inspired by and partially based on the excellent work in [`duckduckgo-mcp-server`](https://github.com/nickclyde/duckduckgo-mcp-server) by [@nickclyde](https://github.com/nickclyde). That project laid the groundwork for integrating DuckDuckGo search and content fetching into the MCP ecosystem.

While `brave-mcp-langchain` extends the concept to support Brave Search and LangChain workflows, several architectural ideas and implementation patterns were adapted from `duckduckgo-mcp-server`, which is licensed under the [MIT License](https://github.com/nickclyde/duckduckgo-mcp-server/blob/main/LICENSE).

I'm grateful for the open-source community and contributors who make projects like this possible. If you’re interested in DuckDuckGo-based search tools, definitely check out the original repository!
