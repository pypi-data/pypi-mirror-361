"""MCP server interface for Agent MCP Tools.

This module provides an MCP server that exposes the agent query functionality
as an MCP tool, allowing other agents to use this agent recursively.
"""

import logging
import sys
from pathlib import Path

from fastmcp import FastMCP

from ..config import cli_config
from ..core.executor import query_llm

# Configure logging
logger = logging.getLogger(__name__)

# Create FastMCP instance
mcp = FastMCP(name="Agent MCP Tools Server")


async def query(
    prompt: str,
    conversation_id: str | None = None,
    close_conversation: bool = False,
) -> str:
    """Query an LLM with a prompt and optional settings.

    This function exposes the agent's query functionality as an MCP tool,
    allowing other agents to use this agent's capabilities.

    Args:
        prompt: The user's prompt to the LLM.
        conversation_id: ID of an ongoing conversation.
        close_conversation: If true, closes the conversation.

    Returns:
        The LLM's response to the prompt.
    """
    return await query_llm(
        prompt=prompt,
        system_prompt_file=cli_config.system_prompt_file,
        mcp_config_file=cli_config.mcp_config_file,
        conversation_id=conversation_id,
        close_conversation=close_conversation,
        model=cli_config.model,
        max_tokens=cli_config.max_tokens,
        temperature=cli_config.temperature,
        agent_tool_name=cli_config.tool_name,
    )


def _configure_verbose_logging() -> None:
    """Configure verbose logging for our project only."""
    # Create custom formatter for better readability
    formatter = logging.Formatter(
        fmt='%(message)s'
    )
    
    # Set up stderr handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    
    # Only configure loggers for our project modules
    project_modules = [
        'agent_mcp_tools.core.executor',
        'agent_mcp_tools.core.llm.openrouter',
        'agent_mcp_tools.core.mcp_tool_manager',
        'agent_mcp_tools.interfaces.mcp_server',
        'agent_mcp_tools.interfaces.cli'
    ]
    
    for module_name in project_modules:
        module_logger = logging.getLogger(module_name)
        module_logger.setLevel(logging.DEBUG)
        module_logger.addHandler(handler)
        # Prevent propagation to avoid duplicate logs
        module_logger.propagate = False


def create_mcp_server(
    system_prompt_file: Path | None = None,
    mcp_config_file: Path | None = None,
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    tool_name: str = "query",
    tool_description: str = "Query an LLM with a prompt and optional settings.",
    verbose: bool = False,
) -> FastMCP:
    """Create and configure an MCP server instance.

    Args:
        system_prompt_file: Path to system prompt template file
        mcp_config_file: Path to MCP configuration file
        model: Model to use for generation
        max_tokens: Maximum tokens to generate
        temperature: Temperature for sampling
        tool_name: Name for the query tool
        tool_description: Description for the query tool
        verbose: Enable verbose logging to stderr

    Returns:
        Configured FastMCP server instance
    """
    # Configure verbose logging if enabled
    if verbose:
        _configure_verbose_logging()

    # Update global config
    if system_prompt_file is not None:
        cli_config.system_prompt_file = system_prompt_file
    if mcp_config_file is not None:
        cli_config.mcp_config_file = mcp_config_file
    if model is not None:
        cli_config.model = model
    if max_tokens is not None:
        cli_config.max_tokens = max_tokens
    if temperature is not None:
        cli_config.temperature = temperature
    if tool_name is not None:
        cli_config.tool_name = tool_name
    if tool_description is not None:
        cli_config.tool_description = tool_description

    # Create new server instance with custom name
    server = FastMCP(name="Agent MCP Tools Server")

    # Register the query function with custom name and description
    server.tool(name=tool_name, description=tool_description)(query)

    return server
