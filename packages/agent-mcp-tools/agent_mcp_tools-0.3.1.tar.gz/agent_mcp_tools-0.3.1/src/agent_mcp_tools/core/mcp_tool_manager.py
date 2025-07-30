"""MCP Tool Manager for Agent MCP Tools.

This module provides a centralized manager for MCP tools, handling configuration loading,
server connections, tool listing, and tool execution.

Using a simplified approach that avoids the cancel scope issues by minimizing
async context manager usage and implementing direct connection management.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.stdio import StdioServerParameters, stdio_client

from ..config import ServerConfig, load_mcp_config

logger = logging.getLogger(__name__)

# Constants
DEFAULT_TIMEOUT = 10.0
TOOL_CALL_TIMEOUT = 600.0


def _truncate_content(content: str, max_length: int = 200) -> str:
    """Truncate content for logging while preserving readability."""
    if len(content) <= max_length:
        return content
    return content[:max_length] + "..."


class MCPConnectionError(Exception):
    """Raised when there's an error connecting to MCP server."""
    pass


class ToolConverter:
    """Converts between different tool formats."""

    @staticmethod
    def mcp_to_openai(mcp_tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convert MCP tool definitions to OpenAI-compatible format."""
        openai_tools = []

        for tool in mcp_tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.get("name", "unknown_tool"),
                    "description": tool.get("description", ""),
                    "parameters": {
                        "type": "object",
                        "properties": tool.get("inputSchema", {}).get("properties", {}),
                        "required": tool.get("inputSchema", {}).get("required", []),
                    },
                },
            }
            openai_tools.append(openai_tool)

        return openai_tools


class MCPClient:
    """Manages connection to a single MCP server using simplified connection pattern."""

    def __init__(self, config: ServerConfig):
        self.config = config
        self._tools_cache: list[dict[str, Any]] | None = None

    async def _execute_with_session(self, operation_func):
        """Execute an operation with a temporary session.
        
        This creates a session, executes the operation, and ensures cleanup
        happens in the same task context to avoid cancel scope issues.
        """
        session = None
        transport_context = None
        
        try:
            # Create transport based on configuration
            if self.config.is_sse:
                transport_context = sse_client(self.config.url)
                sse_transport = await transport_context.__aenter__()
                read_stream, write_stream = sse_transport
            elif self.config.is_stdio:
                import os
                env_vars = os.environ.copy()
                env_vars.update(self.config.env)

                server_params = StdioServerParameters(
                    command=self.config.command,
                    args=self.config.args,
                    env=env_vars,
                )
                
                transport_context = stdio_client(server_params)
                stdio_transport = await transport_context.__aenter__()
                read_stream, write_stream = stdio_transport
            else:
                raise MCPConnectionError(f"Invalid server configuration for {self.config.name}")

            # Create and initialize session
            session = ClientSession(read_stream, write_stream)
            await session.__aenter__()
            await asyncio.wait_for(session.initialize(), DEFAULT_TIMEOUT)
            
            # Execute the operation
            result = await operation_func(session)
            return result
            
        except Exception as e:
            logger.exception(f"Error in MCP operation for {self.config.name}: {e}")
            raise
        finally:
            # Clean up in reverse order
            if session:
                try:
                    await session.__aexit__(None, None, None)
                except Exception as e:
                    logger.debug(f"Session cleanup warning for {self.config.name}: {e}")
            
            if transport_context:
                try:
                    await transport_context.__aexit__(None, None, None)
                except Exception as e:
                    logger.debug(f"Transport cleanup warning for {self.config.name}: {e}")

    async def get_tools(self) -> list[dict[str, Any]]:
        """Get tools from the server with caching."""
        if self._tools_cache is not None:
            return self._tools_cache

        async def fetch_tools(session):
            response = await asyncio.wait_for(session.list_tools(), DEFAULT_TIMEOUT)
            tools = self._process_tools_response(response)
            self._tools_cache = tools
            return tools

        try:
            return await self._execute_with_session(fetch_tools)
        except Exception as e:
            logger.exception(f"Error fetching tools from {self.config.name}: {e}")
            return []

    def _process_tools_response(self, response) -> list[dict[str, Any]]:
        """Process the tools response from MCP server."""
        tools = []

        if not response or not hasattr(response, 'tools'):
            return tools

        for tool in response.tools:
            tool_dict = {
                "name": tool.name,
                "description": tool.description or "",
                "inputSchema": self._extract_input_schema(tool),
            }
            tools.append(tool_dict)

        return tools

    def _extract_input_schema(self, tool) -> dict[str, Any]:
        """Extract input schema from tool definition."""
        if not hasattr(tool, 'inputSchema'):
            return {}

        if isinstance(tool.inputSchema, dict):
            return tool.inputSchema

        # Convert from object to dict
        properties = getattr(tool.inputSchema, 'properties', {})
        required = getattr(tool.inputSchema, 'required', [])

        return {
            "properties": properties,
            "required": required,
        }

    async def call_tool(self, tool_name: str, args: dict[str, Any]) -> str:
        """Call a tool on this server using a temporary session."""
        async def execute_tool(session):
            result = await asyncio.wait_for(
                session.call_tool(tool_name, arguments=args),
                TOOL_CALL_TIMEOUT
            )
            return self._extract_content(result)

        try:
            result = await self._execute_with_session(execute_tool)
            return result
        except Exception as e:
            logger.error(f"❌ Tool '{tool_name}' on server '{self.config.name}' failed: {e}")
            raise

    def _extract_content(self, result) -> str:
        """Extract content from tool call result."""
        if not result:
            return "No content returned"

        if not hasattr(result, 'content'):
            return str(result)

        content = result.content

        if isinstance(content, list):
            content_items = []
            for item in content:
                if hasattr(item, 'text'):
                    content_items.append(item.text)
                else:
                    content_items.append(str(item))
            return "\n".join(content_items)

        if hasattr(content, 'text'):
            return content.text

        return str(content)

    async def test_connection(self) -> bool:
        """Test if we can connect to the server."""
        async def test_session(session):
            # If we can create and initialize a session, connection works
            return True

        try:
            return await self._execute_with_session(test_session)
        except Exception as e:
            logger.exception(f"Failed to connect to MCP server {self.config.name}: {e}")
            return False

    async def disconnect(self) -> None:
        """Disconnect from the server (clear cache)."""
        self._tools_cache = None


class MCPToolManager:
    """Centralized manager for MCP tools using simplified connection pattern."""

    def __init__(self, agent_tool_name: str | None = None):
        self.clients: dict[str, MCPClient] = {}
        self.server_configs: dict[str, ServerConfig] = {}
        self.agent_tool_name = agent_tool_name or "agent"

    async def load_from_file(self, config_path: Path) -> None:
        """Load MCP configuration from file and test server connections.

        Args:
            config_path: Path to the MCP configuration JSON file

        Raises:
            ConfigurationError: If the configuration file is invalid
        """
        self.server_configs = load_mcp_config(config_path)
        await self._test_server_connections()

    async def _test_server_connections(self) -> None:
        """Test connections to all configured MCP servers."""
        for name, config in self.server_configs.items():
            client = MCPClient(config)
            # Test the connection but don't maintain it
            if await client.test_connection():
                self.clients[name] = client
            else:
                logger.warning(f"⚠️ [{self.agent_tool_name}] MCP server '{name}' unavailable")

    async def list_tools(self) -> list[dict[str, Any]]:
        """List all available tools from all connected servers.

        Returns:
            List of tool definitions in MCP format
        """
        all_tools = []

        for server_name, client in self.clients.items():
            tools = await client.get_tools()
            all_tools.extend(tools)
        
        return all_tools

    async def call_tool(self, tool_name: str, args: dict[str, Any]) -> str:
        """Call a tool by name with the given arguments.

        Args:
            tool_name: Name of the tool to call
            args: Arguments to pass to the tool

        Returns:
            Tool execution result as string

        Raises:
            MCPConnectionError: If no server has the requested tool
        """
        # Find which server has this tool
        for server_name, client in self.clients.items():
            tools = await client.get_tools()
            if any(tool["name"] == tool_name for tool in tools):
                try:
                    result = await client.call_tool(tool_name, args)
                    logger.info(f"🔧 [{self.agent_tool_name}] {tool_name} | Result: {_truncate_content(str(result), 100)}")
                    return result
                except Exception as e:
                    logger.error(f"❌ [{self.agent_tool_name}] {tool_name} | Failed: {e}")
                    raise

        available_tools = []
        for client in self.clients.values():
            tools = await client.get_tools()
            available_tools.extend([tool["name"] for tool in tools])
        
        error_msg = f"Tool '{tool_name}' not found. Available: {available_tools}"
        logger.error(f"❌ [{self.agent_tool_name}] {error_msg}")
        raise MCPConnectionError(error_msg)

    async def cleanup(self) -> None:
        """Clean up all connections."""
        # Clear all caches and reset state
        for client in self.clients.values():
            await client.disconnect()
        
        # Clear the collections
        self.clients.clear()
        self.server_configs.clear()
