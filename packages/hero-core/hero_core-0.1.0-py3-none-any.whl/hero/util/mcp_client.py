import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from contextlib import AsyncExitStack
import os
import json
from util import log, config


class MCPClient:
    """
    MCP 客户端
    """
    def __init__(self):
        self.servers = {}
        self.stack = AsyncExitStack()

        with open(
            os.path.join(os.path.dirname(__file__), "../mcp_server.json"),
            "r",
            encoding="utf-8",
        ) as f:
            self.mcp_server_config = json.load(f)["mcpServers"]

        self.mcp_servers_enabled = config.get("mcp_servers_enabled")
        log.debug(f"mcp_servers_enabled: {self.mcp_servers_enabled}")

    def server_is_enabled(self, server_name):
        """
        服务器是否启用
        """
        return server_name in self.mcp_servers_enabled

    async def connect(self):
        """
        连接服务器
        """
        for k, v in self.mcp_server_config.items():
            if not self.server_is_enabled(k):
                continue
            self.servers[k] = {}
            stdio_transport = await self.stack.enter_async_context(
                stdio_client(
                    StdioServerParameters(
                        command=v["command"],
                        args=v["args"],
                        env=v["env"] if "env" in v else None,
                    )
                )
            )
            read, write = stdio_transport
            self.servers[k]["session"] = await self.stack.enter_async_context(
                ClientSession(read, write)
            )
            await self.servers[k]["session"].initialize()

    async def list_all_tools(self):
        """
        列出所有工具
        """
        available_tools = []
        for server in self.servers.values():
            response = await server["session"].list_tools()
            for tool in response.tools:
                available_tools.append(
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema,
                    }
                )
        return available_tools

    async def call_tool(self, tool_name, tool_input):
        """
        调用工具
        """
        for server in self.servers.values():
            response = await server["session"].call_tool(tool_name, tool_input)
            return response

    async def close(self):
        """
        关闭客户端
        """
        try:
            await self.stack.aclose()
        except Exception as e:
            log.error(f"Error during cleanup: {e}")
        finally:
            self.servers.clear()


async def main():
    """
    测试
    """
    client = MCPClient()
    try:
        await client.connect()
        tools = await client.list_all_tools()
        log.debug(tools)
    except Exception as e:
        log.error(f"Error during execution: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())