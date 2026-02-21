"""
CLI interface for interacting with the autonomous coding agent.
"""

import sys
from typing import Optional
from ..agent.controller import AgentController
from ..llm.base import BaseLLM
from ..tools.registry import ToolRegistry
from ..diff.engine import DiffEngine
from .display import Display


class CLI:
    """
    Command-line interface for the autonomous coding agent.
    Handles user interaction, streaming output, and approval workflows.
    """

    def __init__(
        self,
        agent: AgentController,
        display: Optional[Display] = None,
        require_approval: bool = True
    ):
        self.agent = agent
        self.display = display or Display()
        self.require_approval = require_approval
        self.running = True

    def run(self) -> None:
        """Main CLI loop."""
        self.display.print_header("CodiCode - Local Autonomous Coding Agent")
        self.display.print_info("Type your request or 'quit' to exit")
        self.display.print_info("Type 'help' for available commands")

        while self.running:
            try:
                # Get user input
                self.display.print("\n" + ">"*3, None)
                user_input = input().strip()

                if not user_input:
                    continue

                # Handle special commands
                if self._handle_command(user_input):
                    continue

                # Execute task
                self._execute_task(user_input)

            except KeyboardInterrupt:
                self.display.print_warning("\nInterrupted by user")
                if self.display.confirm("Exit?", default=True):
                    self.running = False
            except EOFError:
                self.running = False
            except Exception as e:
                self.display.print_error(f"Unexpected error: {str(e)}")

        self.display.print_info("Goodbye!")

    def _handle_command(self, user_input: str) -> bool:
        """
        Handle special CLI commands.

        Returns:
            True if input was a command, False otherwise
        """
        command = user_input.lower()

        if command in ['quit', 'exit', 'q']:
            self.running = False
            return True

        if command == 'help':
            self._show_help()
            return True

        if command == 'reset':
            self.agent.reset()
            self.display.print_success("Agent state reset")
            return True

        if command == 'status':
            self._show_status()
            return True

        if command == 'tools':
            self._show_tools()
            return True

        return False

    def _execute_task(self, task: str) -> None:
        """Execute a user task."""
        self.display.print_separator()
        self.display.print_info(f"Executing task: {task}")
        self.display.print_separator()

        try:
            # Execute through agent
            result = self.agent.execute_task(task)

            self.display.print_separator()
            self.display.print_success("Task completed")
            self.display.print("\nResult:", None)
            self.display.print(result, None)

        except Exception as e:
            self.display.print_error(f"Task execution failed: {str(e)}")

    def _show_help(self) -> None:
        """Show help information."""
        help_text = """
Available Commands:
  help      - Show this help message
  quit/exit - Exit the application
  reset     - Reset agent state
  status    - Show agent status
  tools     - List available tools

Usage:
  Simply type your coding task in natural language.
  The agent will plan and execute it autonomously.

Examples:
  - Read the file main.py and summarize it
  - Find all Python files in the src/ directory
  - Create a new file called test.py with a hello world function
        """
        self.display.print(help_text, None)

    def _show_status(self) -> None:
        """Show agent status."""
        self.display.print_header("Agent Status")
        self.display.print(f"Steps executed: {self.agent.step_count}", None)
        self.display.print(f"Max steps: {self.agent.max_steps}", None)
        self.display.print(f"Tool errors: {self.agent.tool_error_count}", None)
        self.display.print(f"Task complete: {self.agent.is_task_complete}", None)
        self.display.print(f"Conversation length: {len(self.agent.conversation_history)}", None)

    def _show_tools(self) -> None:
        """Show available tools."""
        self.display.print_header("Available Tools")
        tools = self.agent.tool_registry.list_tools()

        for tool_name in tools:
            tool = self.agent.tool_registry.get_tool(tool_name)
            self.display.print(f"  • {tool_name}", None)
            self.display.print(f"    {tool.description}", None)

    def run_single_task(self, task: str) -> str:
        """
        Run a single task and return the result.
        Useful for scripting or testing.

        Args:
            task: Task description

        Returns:
            Task result
        """
        return self.agent.execute_task(task)


def create_cli(llm: BaseLLM, tool_registry: ToolRegistry) -> CLI:
    """
    Factory function to create a configured CLI instance.

    Args:
        llm: LLM instance
        tool_registry: Tool registry with registered tools

    Returns:
        Configured CLI instance
    """
    agent = AgentController(
        llm=llm,
        tool_registry=tool_registry
    )

    display = Display()
    cli = CLI(agent=agent, display=display)

    return cli
