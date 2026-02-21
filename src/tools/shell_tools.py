"""
Shell command execution tools.
"""

import subprocess
import shlex
from typing import Any, Dict
from .base import BaseTool, ToolResult


class RunShellTool(BaseTool):
    """
    Tool for executing shell commands.
    Runs commands in a sandbox-safe manner with timeout.
    """

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    @property
    def name(self) -> str:
        return "run_shell"

    @property
    def description(self) -> str:
        return "Execute a shell command and return its output. Use with caution."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute"
                },
                "working_dir": {
                    "type": "string",
                    "description": "Working directory for command execution (optional)"
                }
            },
            "required": ["command"]
        }

    def execute(self, command: str, working_dir: str = None) -> ToolResult:
        """Execute a shell command."""
        try:
            # Security: validate command doesn't contain dangerous patterns
            if self._is_dangerous_command(command):
                return ToolResult(
                    success=False,
                    error="Command rejected: potentially dangerous operation detected"
                )

            # Execute the command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=working_dir
            )

            # Combine stdout and stderr
            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"

            if not output:
                output = "(no output)"

            # Check return code
            if result.returncode != 0:
                return ToolResult(
                    success=False,
                    data=output,
                    error=f"Command exited with code {result.returncode}"
                )

            return ToolResult(
                success=True,
                data=output
            )

        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                error=f"Command timed out after {self.timeout} seconds"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error executing command: {str(e)}"
            )

    def _is_dangerous_command(self, command: str) -> bool:
        """
        Basic safety check for dangerous commands.
        This is not comprehensive - for production, use proper sandboxing.
        """
        dangerous_patterns = [
            'rm -rf /',
            'mkfs',
            'dd if=',
            '> /dev/sda',
            'format c:',
            'del /f /s /q',
            'chmod 777 /',
            'chown -R'
        ]

        command_lower = command.lower()
        return any(pattern in command_lower for pattern in dangerous_patterns)


class GetWorkingDirectoryTool(BaseTool):
    """Tool for getting the current working directory."""

    @property
    def name(self) -> str:
        return "get_working_directory"

    @property
    def description(self) -> str:
        return "Get the current working directory"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {}
        }

    def execute(self) -> ToolResult:
        """Get current working directory."""
        try:
            import os
            cwd = os.getcwd()
            return ToolResult(
                success=True,
                data=cwd
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error getting working directory: {str(e)}"
            )
