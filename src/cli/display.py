"""
Display utilities for CLI output formatting.
"""

import sys
from typing import Optional


class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"


class Display:
    """
    Handles formatted output to the terminal.
    Provides methods for printing with colors, formatting diffs, etc.
    """

    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors and sys.stdout.isatty()

    def print(self, message: str, color: Optional[str] = None) -> None:
        """Print a message with optional color."""
        if self.use_colors and color:
            print(f"{color}{message}{Colors.RESET}")
        else:
            print(message)

    def print_header(self, message: str) -> None:
        """Print a section header."""
        self.print(f"\n{'='*60}", Colors.CYAN)
        self.print(f"{message}", Colors.CYAN + Colors.BOLD)
        self.print(f"{'='*60}", Colors.CYAN)

    def print_success(self, message: str) -> None:
        """Print a success message."""
        self.print(f"✓ {message}", Colors.GREEN)

    def print_error(self, message: str) -> None:
        """Print an error message."""
        self.print(f"✗ {message}", Colors.RED)

    def print_warning(self, message: str) -> None:
        """Print a warning message."""
        self.print(f"⚠ {message}", Colors.YELLOW)

    def print_info(self, message: str) -> None:
        """Print an info message."""
        self.print(f"ℹ {message}", Colors.BLUE)

    def print_diff(self, diff: str) -> None:
        """Print a diff with syntax highlighting."""
        self.print("\n--- Diff Preview ---", Colors.CYAN)

        for line in diff.split('\n'):
            if line.startswith('+++') or line.startswith('---'):
                self.print(line, Colors.BOLD)
            elif line.startswith('@@'):
                self.print(line, Colors.CYAN)
            elif line.startswith('+'):
                self.print(line, Colors.GREEN)
            elif line.startswith('-'):
                self.print(line, Colors.RED)
            else:
                self.print(line, Colors.DIM)

        self.print("--- End Diff ---\n", Colors.CYAN)

    def print_tool_call(self, tool_name: str, arguments: dict) -> None:
        """Print a tool call notification."""
        self.print(f"\n🔧 Calling tool: {tool_name}", Colors.MAGENTA)
        if arguments:
            self.print(f"   Arguments: {arguments}", Colors.DIM)

    def print_tool_result(self, success: bool, message: str) -> None:
        """Print tool execution result."""
        if success:
            self.print_success(f"Tool result: {message}")
        else:
            self.print_error(f"Tool failed: {message}")

    def stream_text(self, text: str, end: str = '') -> None:
        """Stream text output character by character or chunk by chunk."""
        print(text, end=end, flush=True)

    def prompt_user(self, message: str, default: Optional[str] = None) -> str:
        """Prompt user for input."""
        if default:
            prompt = f"{message} [{default}]: "
        else:
            prompt = f"{message}: "

        self.print(prompt, Colors.YELLOW)
        response = input().strip()

        if not response and default:
            return default

        return response

    def confirm(self, message: str, default: bool = False) -> bool:
        """Ask user for yes/no confirmation."""
        default_str = "Y/n" if default else "y/N"
        response = self.prompt_user(f"{message} ({default_str})", "")

        if not response:
            return default

        return response.lower() in ['y', 'yes']

    def print_separator(self) -> None:
        """Print a visual separator line."""
        self.print("-" * 60, Colors.GRAY)

    def clear_line(self) -> None:
        """Clear the current line."""
        if self.use_colors:
            print("\r\033[K", end='')

    def print_step(self, step_num: int, total_steps: int, description: str) -> None:
        """Print a step indicator."""
        self.print(f"\n[{step_num}/{total_steps}] {description}", Colors.CYAN)
