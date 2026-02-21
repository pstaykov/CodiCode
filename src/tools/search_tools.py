"""
Search tools for finding files and content in codebase.
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List
from .base import BaseTool, ToolResult


class GrepSearchTool(BaseTool):
    """Tool for searching text patterns in files."""

    @property
    def name(self) -> str:
        return "grep_search"

    @property
    def description(self) -> str:
        return "Search for a text pattern in files within a directory"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Text pattern or regex to search for"
                },
                "directory": {
                    "type": "string",
                    "description": "Directory to search in (default: current directory)"
                },
                "file_pattern": {
                    "type": "string",
                    "description": "Filter files by pattern (e.g., '*.py')"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 50
                }
            },
            "required": ["pattern"]
        }

    def execute(
        self,
        pattern: str,
        directory: str = ".",
        file_pattern: str = "*",
        max_results: int = 50
    ) -> ToolResult:
        """Search for pattern in files."""
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return ToolResult(
                    success=False,
                    error=f"Directory not found: {directory}"
                )

            # Compile regex pattern
            try:
                regex = re.compile(pattern)
            except re.error as e:
                return ToolResult(
                    success=False,
                    error=f"Invalid regex pattern: {str(e)}"
                )

            # Search files
            results = []
            files_searched = 0

            for file_path in dir_path.rglob(file_pattern):
                if not file_path.is_file():
                    continue

                # Skip binary files and large files
                if file_path.stat().st_size > 1_000_000:  # Skip files > 1MB
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                results.append({
                                    "file": str(file_path.relative_to(dir_path)),
                                    "line": line_num,
                                    "content": line.strip()
                                })

                                if len(results) >= max_results:
                                    break

                    files_searched += 1

                except (UnicodeDecodeError, PermissionError):
                    # Skip binary or inaccessible files
                    continue

                if len(results) >= max_results:
                    break

            # Format results
            if not results:
                return ToolResult(
                    success=True,
                    data=f"No matches found for '{pattern}' (searched {files_searched} files)"
                )

            output_lines = [f"Found {len(results)} matches:"]
            for result in results:
                output_lines.append(
                    f"{result['file']}:{result['line']}: {result['content']}"
                )

            return ToolResult(
                success=True,
                data="\n".join(output_lines)
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error during search: {str(e)}"
            )


class FindFilesTool(BaseTool):
    """Tool for finding files by name pattern."""

    @property
    def name(self) -> str:
        return "find_files"

    @property
    def description(self) -> str:
        return "Find files matching a name pattern in a directory tree"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "File name pattern (e.g., '*.py', 'test_*.js')"
                },
                "directory": {
                    "type": "string",
                    "description": "Directory to search in (default: current directory)"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 100
                }
            },
            "required": ["pattern"]
        }

    def execute(
        self,
        pattern: str,
        directory: str = ".",
        max_results: int = 100
    ) -> ToolResult:
        """Find files by name pattern."""
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return ToolResult(
                    success=False,
                    error=f"Directory not found: {directory}"
                )

            # Search for files
            files = []
            for file_path in dir_path.rglob(pattern):
                if file_path.is_file():
                    files.append(str(file_path.relative_to(dir_path)))

                if len(files) >= max_results:
                    break

            if not files:
                return ToolResult(
                    success=True,
                    data=f"No files found matching '{pattern}'"
                )

            return ToolResult(
                success=True,
                data="\n".join(files)
            )

        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error finding files: {str(e)}"
            )
