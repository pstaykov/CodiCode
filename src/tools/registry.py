"""
Tool registry for managing and executing tools.
Provides a central place to register and invoke tools.
"""

from typing import Dict, List, Optional
from .base import BaseTool, ToolResult


class ToolRegistry:
    """
    Centralized registry for all available tools.
    Handles tool registration, lookup, and execution.
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._execution_log: List[Dict] = []

    def register(self, tool: BaseTool) -> None:
        """
        Register a tool in the registry.

        Args:
            tool: Tool instance to register
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")

        self._tools[tool.name] = tool
        print(f"[ToolRegistry] Registered tool: {tool.name}")

    def register_all(self, tools: List[BaseTool]) -> None:
        """Register multiple tools at once."""
        for tool in tools:
            self.register(tool)

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """Get list of all registered tool names."""
        return list(self._tools.keys())

    def get_tools_for_llm(self) -> List[Dict]:
        """
        Get all tools in LLM function calling format.
        Used to tell the LLM what tools are available.
        """
        return [tool.to_llm_format() for tool in self._tools.values()]

    def execute(self, tool_name: str, **kwargs) -> ToolResult:
        """
        Execute a tool by name with given parameters.

        Args:
            tool_name: Name of the tool to execute
            **kwargs: Parameters for the tool

        Returns:
            ToolResult with execution outcome
        """
        tool = self.get_tool(tool_name)

        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' not found. Available: {self.list_tools()}"
            )

        # Log the execution
        log_entry = {
            "tool": tool_name,
            "parameters": kwargs
        }

        try:
            print(f"[ToolRegistry] Executing: {tool_name}")
            result = tool.execute(**kwargs)
            log_entry["result"] = result.to_dict()
            self._execution_log.append(log_entry)
            return result

        except Exception as e:
            error_result = ToolResult(
                success=False,
                error=f"Tool execution failed: {str(e)}"
            )
            log_entry["result"] = error_result.to_dict()
            self._execution_log.append(log_entry)
            return error_result

    def get_execution_log(self) -> List[Dict]:
        """Get history of all tool executions."""
        return self._execution_log.copy()

    def clear_log(self) -> None:
        """Clear execution log."""
        self._execution_log.clear()


# Global registry instance
_global_registry = None


def get_registry() -> ToolRegistry:
    """Get or create the global tool registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry
