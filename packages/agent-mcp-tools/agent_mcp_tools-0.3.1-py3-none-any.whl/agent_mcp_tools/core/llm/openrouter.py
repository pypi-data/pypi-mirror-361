"""OpenRouter LLM provider implementation.

This module provides the OpenRouter-specific implementation of the LLM client.
"""

import logging
from typing import Any

import httpx

from .base import LLMClient, LLMProviderError

logger = logging.getLogger(__name__)

# Constants
API_REQUEST_TIMEOUT = 120.0


class OpenRouterClient(LLMClient):
    """Handles communication with OpenRouter API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://localhost",
            "X-Title": "Agent MCP Tools",
            "Content-Type": "application/json",
        }

    async def chat_completion(
        self,
        messages: list[dict[str, Any]],
        model: str,
        max_tokens: int,
        temperature: float,
        tools: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """Send a chat completion request to OpenRouter."""
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=API_REQUEST_TIMEOUT,
            )

            if response.status_code != 200:
                error_msg = f"OpenRouter API error: {response.status_code} - {response.text}"
                logger.error(f"❌ {error_msg}")
                raise LLMProviderError(error_msg)

            response_data = response.json()
            return response_data
