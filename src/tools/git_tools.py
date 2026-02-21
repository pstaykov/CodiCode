"""
Git integration tools for version control operations.
"""

import subprocess
from pathlib import Path
from typing import Any, Dict, List
from .base import BaseTool, ToolResult


class GitStatusTool(BaseTool):
    """Get git repository status."""

    @property
    def name(self) -> str:
        return "git_status"

    @property
    def description(self) -> str:
        return "Get the status of the git repository"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Repository directory (default: current)"
                }
            }
        }

    def execute(self, directory: str = ".") -> ToolResult:
        """Get git status."""
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return ToolResult(
                    success=False,
                    error=f"Git error: {result.stderr}"
                )

            output = result.stdout.strip()
            if not output:
                output = "Working directory clean"

            return ToolResult(success=True, data=output)

        except FileNotFoundError:
            return ToolResult(success=False, error="Git not installed")
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class GitDiffTool(BaseTool):
    """Show git diff."""

    @property
    def name(self) -> str:
        return "git_diff"

    @property
    def description(self) -> str:
        return "Show git diff for changed files"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Specific file to diff (optional)"
                },
                "staged": {
                    "type": "boolean",
                    "description": "Show staged changes only"
                },
                "directory": {
                    "type": "string",
                    "description": "Repository directory"
                }
            }
        }

    def execute(
        self,
        file_path: str = None,
        staged: bool = False,
        directory: str = "."
    ) -> ToolResult:
        """Show git diff."""
        try:
            cmd = ["git", "diff"]

            if staged:
                cmd.append("--staged")

            if file_path:
                cmd.append(file_path)

            result = subprocess.run(
                cmd,
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return ToolResult(
                    success=False,
                    error=f"Git error: {result.stderr}"
                )

            output = result.stdout.strip()
            if not output:
                output = "(no changes)"

            return ToolResult(success=True, data=output)

        except Exception as e:
            return ToolResult(success=False, error=str(e))


class GitLogTool(BaseTool):
    """Show git commit history."""

    @property
    def name(self) -> str:
        return "git_log"

    @property
    def description(self) -> str:
        return "Show git commit history"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "max_count": {
                    "type": "integer",
                    "description": "Maximum number of commits to show",
                    "default": 10
                },
                "file_path": {
                    "type": "string",
                    "description": "Show history for specific file"
                },
                "directory": {
                    "type": "string",
                    "description": "Repository directory"
                }
            }
        }

    def execute(
        self,
        max_count: int = 10,
        file_path: str = None,
        directory: str = "."
    ) -> ToolResult:
        """Show git log."""
        try:
            cmd = [
                "git", "log",
                f"--max-count={max_count}",
                "--pretty=format:%h - %an, %ar : %s"
            ]

            if file_path:
                cmd.append(file_path)

            result = subprocess.run(
                cmd,
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return ToolResult(
                    success=False,
                    error=f"Git error: {result.stderr}"
                )

            return ToolResult(success=True, data=result.stdout.strip())

        except Exception as e:
            return ToolResult(success=False, error=str(e))


class GitBranchTool(BaseTool):
    """List or create git branches."""

    @property
    def name(self) -> str:
        return "git_branch"

    @property
    def description(self) -> str:
        return "List git branches or create a new branch"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "create"],
                    "description": "Action to perform",
                    "default": "list"
                },
                "branch_name": {
                    "type": "string",
                    "description": "Branch name (for create action)"
                },
                "directory": {
                    "type": "string",
                    "description": "Repository directory"
                }
            }
        }

    def execute(
        self,
        action: str = "list",
        branch_name: str = None,
        directory: str = "."
    ) -> ToolResult:
        """Manage git branches."""
        try:
            if action == "list":
                cmd = ["git", "branch", "-a"]
            elif action == "create":
                if not branch_name:
                    return ToolResult(
                        success=False,
                        error="branch_name required for create action"
                    )
                cmd = ["git", "branch", branch_name]
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown action: {action}"
                )

            result = subprocess.run(
                cmd,
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return ToolResult(
                    success=False,
                    error=f"Git error: {result.stderr}"
                )

            output = result.stdout.strip()
            if action == "create":
                output = f"Created branch: {branch_name}"

            return ToolResult(success=True, data=output)

        except Exception as e:
            return ToolResult(success=False, error=str(e))


class GitCommitTool(BaseTool):
    """Create a git commit."""

    @property
    def name(self) -> str:
        return "git_commit"

    @property
    def description(self) -> str:
        return "Stage and commit changes to git"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Commit message"
                },
                "files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Files to stage (empty = all changes)"
                },
                "directory": {
                    "type": "string",
                    "description": "Repository directory"
                }
            },
            "required": ["message"]
        }

    def execute(
        self,
        message: str,
        files: List[str] = None,
        directory: str = "."
    ) -> ToolResult:
        """Create commit."""
        try:
            # Stage files
            if files:
                for file in files:
                    subprocess.run(
                        ["git", "add", file],
                        cwd=directory,
                        check=True,
                        capture_output=True
                    )
            else:
                subprocess.run(
                    ["git", "add", "-A"],
                    cwd=directory,
                    check=True,
                    capture_output=True
                )

            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return ToolResult(
                    success=False,
                    error=f"Commit failed: {result.stderr}"
                )

            return ToolResult(
                success=True,
                data=f"Committed: {message}\n{result.stdout}"
            )

        except subprocess.CalledProcessError as e:
            return ToolResult(
                success=False,
                error=f"Git error: {e.stderr.decode() if e.stderr else str(e)}"
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))
