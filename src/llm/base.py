"""
Abstract LLM interface for pluggable model backends.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Iterator, Optional
from dataclasses import dataclass


@dataclass
class Message:
    """Represents a chat message."""
    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class ToolCall:
    """Represents a tool call from the LLM."""
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class LLMResponse:
    """Response from LLM including content and optional tool calls."""
    content: str
    tool_calls: List[ToolCall] = None
    finish_reason: str = "stop"
    tokens_used: int = 0

    def has_tool_calls(self) -> bool:
        """Check if response contains tool calls."""
        return self.tool_calls is not None and len(self.tool_calls) > 0


class BaseLLM(ABC):
    """
    Abstract base class for LLM backends.
    Implementations for Ollama, llama.cpp, vLLM, etc. should inherit this.
    """

    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.config = kwargs
        self.total_tokens_used = 0

    @abstractmethod
    def generate(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            messages: Conversation history
            tools: Available tools in function calling format
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            LLMResponse with content and optional tool calls
        """
        pass

    @abstractmethod
    def generate_stream(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Iterator[str]:
        """
        Generate a streaming response from the LLM.

        Args:
            messages: Conversation history
            tools: Available tools
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Text chunks as they are generated
        """
        pass

    def update_token_count(self, tokens: int) -> None:
        """Track total tokens used."""
        self.total_tokens_used += tokens

    def get_token_count(self) -> int:
        """Get total tokens used."""
        return self.total_tokens_used

    def reset_token_count(self) -> None:
        """Reset token counter."""
        self.total_tokens_used = 0
