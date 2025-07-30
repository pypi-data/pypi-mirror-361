import sys
import os
# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

import traceback

from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent
import anyio

from util import log, config
from tool.search import Search


mcp = Server("mcp_server")

base_url = config.search("base_url")
API_KEY = config.search("api_key")
NUM_RESULTS = config.get("search_results_limit")

@mcp.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent]:
    try:
        log.debug(f"arguments: {arguments}")
        if name == "search":
            search = Search()
            return await search.execute(arguments, arguments.get("caller"))

    except Exception as e:
        log.error(f"Error in search: {e}")
        log.error(traceback.format_exc())
        return [TextContent(type="text", text=f"Error in search: {e}")]

@mcp.list_tools()
async def list_tools():
    return [
        Tool(
            name="search",
            description="Search the web for information",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        )
    ]

if __name__ == "__main__":
    async def arun():
        async with stdio_server() as streams:
            await mcp.run(
                streams[0], streams[1], mcp.create_initialization_options()
            )

    anyio.run(arun)