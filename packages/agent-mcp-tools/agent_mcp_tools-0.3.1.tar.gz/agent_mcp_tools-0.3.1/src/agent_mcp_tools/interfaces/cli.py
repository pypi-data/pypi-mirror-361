"""Command-line interface for Agent MCP Tools.

This module provides a CLI for interacting with LLMs through various providers
and MCP tools, using the refactored core components.
"""

import asyncio
import json
import logging
import os
import sys
import traceback
from enum import Enum
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown

from ..config import DEFAULT_MAX_TOKENS, DEFAULT_MODEL, DEFAULT_TEMPERATURE
from ..core.executor import query_llm
from .mcp_server import create_mcp_server

# Configure logging
logger = logging.getLogger(__name__)

app = typer.Typer()
console = Console()


class ThemeEnum(str, Enum):
    """Enum for available syntax highlighting themes."""
    default = "default"
    monokai = "monokai"
    solarized_light = "solarized-light"
    solarized_dark = "solarized-dark"
    github_dark = "github-dark"
    lightbulb = "lightbulb"


def verify_api_key() -> None:
    """Verify that the OpenRouter API key is set.

    Raises:
        SystemExit: If the API key is not set
    """
    if not os.environ.get("OPENROUTER_API_KEY"):
        typer.echo("Error: OPENROUTER_API_KEY environment variable not set")
        typer.echo("Please run: export OPENROUTER_API_KEY=your_key_here")
        sys.exit(1)


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


@app.command()
def query(
    prompt: str = typer.Argument(..., help="The prompt to send to the LLM"),
    system_prompt: Path = typer.Option(
        None,
        "--system-prompt", "-s",
        help="Path to file containing the system prompt template",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    mcp_config: Path = typer.Option(
        None,
        "--mcp-config", "-m",
        help="Path to MCP configuration JSON file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    model: str = typer.Option(
        DEFAULT_MODEL,
        "--model",
        help="Model to use for generation",
    ),
    max_tokens: int = typer.Option(
        DEFAULT_MAX_TOKENS,
        "--max-tokens",
        help="Maximum number of tokens to generate",
    ),
    temperature: float = typer.Option(
        DEFAULT_TEMPERATURE,
        "--temperature",
        help="Temperature for sampling (0.0 to 1.0)",
        min=0.0,
        max=2.0,
    ),
    theme: ThemeEnum = typer.Option(
        ThemeEnum.monokai,
        "--theme",
        "-t",
        help="Theme for syntax highlighting.",
        case_sensitive=False,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output.",
    ),
) -> None:
    """Query an LLM with optional MCP tools and custom system prompt.

    Args:
        prompt: The prompt text to send to the LLM
        system_prompt: Path to system prompt template file
        mcp_config: Path to MCP configuration JSON file
        model: Model to use
        max_tokens: Maximum tokens to generate
        temperature: Temperature for sampling
        theme: Theme for syntax highlighting
        verbose: Enable verbose logging
    """
    if verbose:
        _configure_verbose_logging()

    verify_api_key()

    # Show configuration
    typer.echo(f"Model: {model}")
    if system_prompt:
        typer.echo(f"System prompt: {system_prompt}")
    if mcp_config:
        typer.echo(f"MCP config: {mcp_config}")
    typer.echo(f"Max tokens: {max_tokens}")
    typer.echo(f"Temperature: {temperature}")
    typer.echo(f"Theme: {theme.value}")
    typer.echo("\nQuerying...\n")

    try:
        result = asyncio.run(query_llm(
            prompt=prompt,
            system_prompt_file=system_prompt,
            mcp_config_file=mcp_config,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
        ))

        console.print("\nResponse:")
        console.print("=" * 50)
        try:
            data = json.loads(result)
            if 'result' in data and isinstance(data['result'], str):
                console.print(Markdown(data['result'], code_theme=theme.value))
            else:
                console.print_json(data=data)
        except (json.JSONDecodeError, TypeError):
            console.print(Markdown(result, code_theme=theme.value))
        console.print("=" * 50)
    except KeyboardInterrupt:
        typer.echo("\nOperation cancelled by user.")
    except Exception as e:
        typer.echo(f"\nError: {e}")
        if logger.isEnabledFor(logging.DEBUG):
            traceback.print_exc()


@app.command()
def stdio(
    system_prompt: Path = typer.Option(
        None,
        "--system-prompt",
        "-s",
        help="Path to file containing the system prompt template",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    mcp_config: Path = typer.Option(
        None,
        "--mcp-config",
        "-m",
        help="Path to MCP configuration JSON file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    model: str = typer.Option(
        DEFAULT_MODEL,
        "--model",
        help="Model to use for generation",
    ),
    max_tokens: int = typer.Option(
        DEFAULT_MAX_TOKENS,
        "--max-tokens",
        help="Maximum number of tokens to generate",
    ),
    temperature: float = typer.Option(
        DEFAULT_TEMPERATURE,
        "--temperature",
        help="Temperature for sampling (0.0 to 1.0)",
        min=0.0,
        max=2.0,
    ),
    tool_name: str = typer.Option(
        "query",
        "--tool-name",
        help="Name for the query tool",
    ),
    tool_description: str = typer.Option(
        "Query an LLM with a prompt and optional settings.",
        "--tool-description",
        help="Description for the query tool",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output.",
    ),
):
    """Run Agent MCP Tools as an MCP server using stdio transport.

    Args:
        system_prompt: Path to system prompt template file
        mcp_config: Path to MCP configuration JSON file
        model: Model to use
        max_tokens: Maximum tokens to generate
        temperature: Temperature for sampling
        tool_name: Name for the query tool
        tool_description: Description for the query tool
        verbose: Enable verbose logging
    """
    verify_api_key()

    # Create and configure MCP server
    server = create_mcp_server(
        system_prompt_file=system_prompt,
        mcp_config_file=mcp_config,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        tool_name=tool_name,
        tool_description=tool_description,
        verbose=verbose,
    )

    # Run server with stdio transport
    server.run()


@app.command()
def http(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind the server to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind the server to"),
    system_prompt: Path = typer.Option(
        None,
        "--system-prompt",
        "-s",
        help="Path to file containing the system prompt template",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    mcp_config: Path = typer.Option(
        None,
        "--mcp-config",
        "-m",
        help="Path to MCP configuration JSON file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    model: str = typer.Option(
        DEFAULT_MODEL,
        "--model",
        help="Model to use for generation",
    ),
    max_tokens: int = typer.Option(
        DEFAULT_MAX_TOKENS,
        "--max-tokens",
        help="Maximum number of tokens to generate",
    ),
    temperature: float = typer.Option(
        DEFAULT_TEMPERATURE,
        "--temperature",
        help="Temperature for sampling (0.0 to 1.0)",
        min=0.0,
        max=2.0,
    ),
    tool_name: str = typer.Option(
        "query",
        "--tool-name",
        help="Name for the query tool",
    ),
    tool_description: str = typer.Option(
        "Query an LLM with a prompt and optional settings.",
        "--tool-description",
        help="Description for the query tool",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output.",
    ),
):
    """Run Agent MCP Tools as an HTTP server.

    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        system_prompt: Path to system prompt template file
        mcp_config: Path to MCP configuration JSON file
        model: Model to use
        max_tokens: Maximum tokens to generate
        temperature: Temperature for sampling
        tool_name: Name for the query tool
        tool_description: Description for the query tool
        verbose: Enable verbose logging
    """
    verify_api_key()

    # Create and configure MCP server
    server = create_mcp_server(
        system_prompt_file=system_prompt,
        mcp_config_file=mcp_config,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        tool_name=tool_name,
        tool_description=tool_description,
        verbose=verbose,
    )

    typer.echo(f"Starting HTTP server on {host}:{port}")

    # Run server with HTTP transport
    server.run(transport="httpx", host=host, port=port)


@app.command()
def examples() -> None:
    """Show usage examples for Agent MCP Tools."""
    examples_text = """
# Agent MCP Tools Examples

## Basic Query
```bash
agent-mcp-tools query "What is the capital of France?"
```

## With System Prompt
```bash
agent-mcp-tools query "Explain quantum computing" --system-prompt system.txt
```

## With MCP Tools
```bash
agent-mcp-tools query "Search for recent news about AI" --mcp-config mcp.json
```

## Custom Model and Parameters
```bash
agent-mcp-tools query "Write a poem" --model "anthropic/claude-3-haiku" --max-tokens 500 --temperature 0.8
```

## Run as MCP Server (stdio)
```bash
agent-mcp-tools stdio --system-prompt system.txt --mcp-config mcp.json
```

## Run as MCP Server with Verbose Logging
```bash
agent-mcp-tools stdio --system-prompt system.txt --mcp-config mcp.json --verbose
```

## Run as HTTP Server
```bash
agent-mcp-tools http --host 0.0.0.0 --port 8080 --system-prompt system.txt
```

## Run as HTTP Server with Verbose Logging
```bash
agent-mcp-tools http --host 0.0.0.0 --port 8080 --system-prompt system.txt --verbose
```

## MCP Configuration Format
Create a `mcp.json` file:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"]
    },
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your-brave-api-key"
      }
    }
  }
}
```

## Environment Variables
```bash
export OPENROUTER_API_KEY=your_openrouter_api_key
```
"""

    console.print(Markdown(examples_text))


def main() -> None:
    """Main entry point for the CLI."""
    app()
