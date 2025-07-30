"""Abstract base class for LLM providers.

This module defines the interface that all LLM providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Any


class LLMProviderError(Exception):
    """Raised when there's an error with the LLM provider."""
    pass


class LLMClient(ABC):
    """Abstract base class for LLM provider clients."""

    @abstractmethod
    async def chat_completion(
        self,
        messages: list[dict[str, Any]],
        model: str,
        max_tokens: int,
        temperature: float,
        tools: list[dict[str, Any]] | None = None
    ) -> dict[str, Any]:
        """Send a chat completion request to the LLM provider.

        Args:
            messages: List of chat messages
            model: Model identifier
            max_tokens: Maximum tokens to generate
            temperature: Temperature for sampling
            tools: Optional list of tools for the model to use

        Returns:
            Response from the LLM provider

        Raises:
            LLMProviderError: If there's an error with the provider
        """
        pass
