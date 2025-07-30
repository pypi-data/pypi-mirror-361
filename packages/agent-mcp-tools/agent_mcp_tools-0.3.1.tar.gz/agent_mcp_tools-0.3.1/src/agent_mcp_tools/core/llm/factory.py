"""Factory for creating LLM clients.

This module provides a factory for creating LLM clients based on configuration.
"""

import os

from .base import LLMClient, LLMProviderError
from .openrouter import OpenRouterClient


class LLMClientFactory:
    """Factory for creating LLM clients based on configuration or environment."""

    @staticmethod
    def create_openrouter_client(api_key: str | None = None) -> LLMClient:
        """Create an OpenRouter client.

        Args:
            api_key: OpenRouter API key. If not provided, will try to get from environment.

        Returns:
            OpenRouter LLM client

        Raises:
            LLMProviderError: If API key is not provided or found in environment
        """
        if api_key is None:
            api_key = os.environ.get("OPENROUTER_API_KEY")

        if not api_key:
            raise LLMProviderError("OpenRouter API key not provided and OPENROUTER_API_KEY environment variable not set")

        return OpenRouterClient(api_key)

    @staticmethod
    def create_default_client(api_key: str | None = None) -> LLMClient:
        """Create the default LLM client (currently OpenRouter).

        Args:
            api_key: API key for the provider

        Returns:
            Default LLM client
        """
        return LLMClientFactory.create_openrouter_client(api_key)
