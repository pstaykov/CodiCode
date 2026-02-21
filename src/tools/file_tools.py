"""
File operation tools for reading, writing, and listing files.
"""

import os
from pathlib import Path
from typing import Any, Dict
from .base import BaseTool, ToolResult


class ReadFileTool(BaseTool):
    """Tool for reading file contents."""

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read the contents of a file at the specified path"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read"
                }
            },
            "required": ["path"]
        }

    def execute(self, path: str) -> ToolResult:
        """Read file contents."""
        try:
            file_path = Path(path)

            if not file_path.exists():
                return ToolResult(
                    success=False,
                    error=f"File not found: {path}"
                )

            if not file_path.is_file():
                return ToolResult(
                    success=False,
                    error=f"Path is not a file: {path}"
                )

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return ToolResult(
                success=True,
                data=content
            )

        except UnicodeDecodeError:
            return ToolResult(
                success=False,
                error=f"File is not text or uses unsupported encoding: {path}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error reading file: {str(e)}"
            )


class WriteFileTool(BaseTool):
    """Tool for writing content to a file."""

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write content to a file at the specified path. Creates parent directories if needed."

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to write"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                }
            },
            "required": ["path", "content"]
        }

    def execute(self, path: str, content: str) -> ToolResult:
        """Write content to file."""
        try:
            file_path = Path(path)

            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return ToolResult(
                success=True,
                data=f"Successfully wrote {len(content)} characters to {path}"
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error writing file: {str(e)}"
            )


class ListDirectoryTool(BaseTool):
    """Tool for listing directory contents."""

    @property
    def name(self) -> str:
        return "list_directory"

    @property
    def description(self) -> str:
        return "List all files and directories in the specified path"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the directory to list"
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Whether to list recursively",
                    "default": False
                }
            },
            "required": ["path"]
        }

    def execute(self, path: str, recursive: bool = False) -> ToolResult:
        """List directory contents."""
        try:
            dir_path = Path(path)

            if not dir_path.exists():
                return ToolResult(
                    success=False,
                    error=f"Directory not found: {path}"
                )

            if not dir_path.is_dir():
                return ToolResult(
                    success=False,
                    error=f"Path is not a directory: {path}"
                )

            if recursive:
                # Recursive listing
                items = []
                for item in dir_path.rglob('*'):
                    rel_path = item.relative_to(dir_path)
                    item_type = "dir" if item.is_dir() else "file"
                    items.append(f"{item_type}: {rel_path}")
            else:
                # Non-recursive listing
                items = []
                for item in sorted(dir_path.iterdir()):
                    item_type = "dir" if item.is_dir() else "file"
                    items.append(f"{item_type}: {item.name}")

            return ToolResult(
                success=True,
                data="\n".join(items) if items else "(empty directory)"
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error listing directory: {str(e)}"
            )


class FileExistsTool(BaseTool):
    """Tool for checking if a file exists."""

    @property
    def name(self) -> str:
        return "file_exists"

    @property
    def description(self) -> str:
        return "Check if a file or directory exists at the specified path"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to check"
                }
            },
            "required": ["path"]
        }

    def execute(self, path: str) -> ToolResult:
        """Check if path exists."""
        try:
            file_path = Path(path)
            exists = file_path.exists()

            if exists:
                item_type = "directory" if file_path.is_dir() else "file"
                return ToolResult(
                    success=True,
                    data=f"Path exists as {item_type}: {path}"
                )
            else:
                return ToolResult(
                    success=True,
                    data=f"Path does not exist: {path}"
                )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error checking path: {str(e)}"
            )
