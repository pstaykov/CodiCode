"""
Base tool interface for the autonomous coding agent.
All tools must inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from dataclasses import dataclass


@dataclass
class ToolResult:
    """Structured result from tool execution."""
    success: bool
    data: Any = None
    error: str = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error
        }


class BaseTool(ABC):
    """
    Abstract base class for all tools.
    Each tool must implement execute() and provide metadata.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name used for invocation."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what the tool does."""
        pass

    @property
    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """
        JSON schema describing tool parameters.

        Example:
        {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"}
            },
            "required": ["path"]
        }
        """
        pass

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with given parameters.

        Args:
            **kwargs: Parameters matching the schema

        Returns:
            ToolResult with success status and data/error
        """
        pass

    def to_llm_format(self) -> Dict[str, Any]:
        """
        Convert tool to LLM-compatible function calling format.
        Used by the LLM layer to understand available tools.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema
            }
        }
