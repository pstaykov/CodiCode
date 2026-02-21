"""
Test execution and validation tools.
"""

import subprocess
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from .base import BaseTool, ToolResult


class PytestRunTool(BaseTool):
    """Run pytest tests."""

    @property
    def name(self) -> str:
        return "run_pytest"

    @property
    def description(self) -> str:
        return "Run Python tests using pytest"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "test_path": {
                    "type": "string",
                    "description": "Path to test file/directory (default: tests/)"
                },
                "verbose": {
                    "type": "boolean",
                    "description": "Verbose output",
                    "default": False
                },
                "collect_only": {
                    "type": "boolean",
                    "description": "Only collect tests, don't run",
                    "default": False
                }
            }
        }

    def execute(
        self,
        test_path: str = "tests/",
        verbose: bool = False,
        collect_only: bool = False
    ) -> ToolResult:
        """Run pytest."""
        try:
            cmd = ["pytest", test_path]

            if verbose:
                cmd.append("-v")

            if collect_only:
                cmd.append("--collect-only")

            # Add JSON report
            cmd.extend(["--tb=short"])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            # Parse output
            output = result.stdout + "\n" + result.stderr

            # Determine success
            success = result.returncode == 0

            if not success:
                return ToolResult(
                    success=False,
                    data=output,
                    error=f"Tests failed (exit code: {result.returncode})"
                )

            return ToolResult(success=True, data=output)

        except FileNotFoundError:
            return ToolResult(
                success=False,
                error="pytest not installed. Install with: pip install pytest"
            )
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                error="Tests timed out after 5 minutes"
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class PythonLintTool(BaseTool):
    """Run Python linter (flake8)."""

    @property
    def name(self) -> str:
        return "lint_python"

    @property
    def description(self) -> str:
        return "Lint Python code using flake8"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to lint (file or directory)"
                },
                "max_line_length": {
                    "type": "integer",
                    "description": "Maximum line length",
                    "default": 88
                }
            },
            "required": ["path"]
        }

    def execute(self, path: str, max_line_length: int = 88) -> ToolResult:
        """Run flake8."""
        try:
            cmd = [
                "flake8",
                path,
                f"--max-line-length={max_line_length}",
                "--statistics"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            output = result.stdout + result.stderr

            if result.returncode == 0:
                return ToolResult(
                    success=True,
                    data="No linting issues found ✓"
                )
            else:
                return ToolResult(
                    success=False,
                    data=output,
                    error=f"Linting issues found"
                )

        except FileNotFoundError:
            return ToolResult(
                success=False,
                error="flake8 not installed. Install with: pip install flake8"
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class PythonFormatTool(BaseTool):
    """Format Python code with black."""

    @property
    def name(self) -> str:
        return "format_python"

    @property
    def description(self) -> str:
        return "Format Python code using black"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to format (file or directory)"
                },
                "check_only": {
                    "type": "boolean",
                    "description": "Only check, don't modify",
                    "default": False
                },
                "line_length": {
                    "type": "integer",
                    "description": "Maximum line length",
                    "default": 88
                }
            },
            "required": ["path"]
        }

    def execute(
        self,
        path: str,
        check_only: bool = False,
        line_length: int = 88
    ) -> ToolResult:
        """Format with black."""
        try:
            cmd = ["black", path, f"--line-length={line_length}"]

            if check_only:
                cmd.append("--check")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            output = result.stdout + result.stderr

            if result.returncode == 0:
                if check_only:
                    return ToolResult(
                        success=True,
                        data="Code is already formatted ✓"
                    )
                else:
                    return ToolResult(
                        success=True,
                        data=f"Formatted: {path}\n{output}"
                    )
            else:
                return ToolResult(
                    success=False,
                    data=output,
                    error="Formatting check failed"
                )

        except FileNotFoundError:
            return ToolResult(
                success=False,
                error="black not installed. Install with: pip install black"
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class TypeCheckTool(BaseTool):
    """Run type checking with mypy."""

    @property
    def name(self) -> str:
        return "type_check"

    @property
    def description(self) -> str:
        return "Check Python types using mypy"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to check"
                },
                "strict": {
                    "type": "boolean",
                    "description": "Enable strict mode",
                    "default": False
                }
            },
            "required": ["path"]
        }

    def execute(self, path: str, strict: bool = False) -> ToolResult:
        """Run mypy."""
        try:
            cmd = ["mypy", path]

            if strict:
                cmd.append("--strict")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            output = result.stdout + result.stderr

            if result.returncode == 0:
                return ToolResult(
                    success=True,
                    data="Type checking passed ✓"
                )
            else:
                return ToolResult(
                    success=False,
                    data=output,
                    error="Type checking failed"
                )

        except FileNotFoundError:
            return ToolResult(
                success=False,
                error="mypy not installed. Install with: pip install mypy"
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class SecurityCheckTool(BaseTool):
    """Run security checks with bandit."""

    @property
    def name(self) -> str:
        return "security_check"

    @property
    def description(self) -> str:
        return "Check Python code for security issues using bandit"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to check"
                },
                "severity": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Minimum severity level",
                    "default": "medium"
                }
            },
            "required": ["path"]
        }

    def execute(self, path: str, severity: str = "medium") -> ToolResult:
        """Run bandit."""
        try:
            cmd = ["bandit", "-r", path, "-f", "txt"]

            # Set severity level
            if severity == "high":
                cmd.extend(["-lll"])
            elif severity == "medium":
                cmd.extend(["-ll"])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            output = result.stdout + result.stderr

            if result.returncode == 0:
                return ToolResult(
                    success=True,
                    data="No security issues found ✓"
                )
            else:
                return ToolResult(
                    success=False,
                    data=output,
                    error="Security issues found"
                )

        except FileNotFoundError:
            return ToolResult(
                success=False,
                error="bandit not installed. Install with: pip install bandit"
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class CodeCoverageTool(BaseTool):
    """Run tests with coverage analysis."""

    @property
    def name(self) -> str:
        return "run_coverage"

    @property
    def description(self) -> str:
        return "Run tests with code coverage using pytest-cov"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "source_path": {
                    "type": "string",
                    "description": "Source code path to measure coverage"
                },
                "test_path": {
                    "type": "string",
                    "description": "Test path",
                    "default": "tests/"
                },
                "min_coverage": {
                    "type": "integer",
                    "description": "Minimum coverage percentage",
                    "default": 80
                }
            },
            "required": ["source_path"]
        }

    def execute(
        self,
        source_path: str,
        test_path: str = "tests/",
        min_coverage: int = 80
    ) -> ToolResult:
        """Run coverage."""
        try:
            cmd = [
                "pytest",
                test_path,
                f"--cov={source_path}",
                f"--cov-fail-under={min_coverage}",
                "--cov-report=term-missing"
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            output = result.stdout + result.stderr

            if result.returncode == 0:
                return ToolResult(
                    success=True,
                    data=output
                )
            else:
                return ToolResult(
                    success=False,
                    data=output,
                    error=f"Coverage below {min_coverage}%"
                )

        except FileNotFoundError:
            return ToolResult(
                success=False,
                error="pytest-cov not installed. Install with: pip install pytest-cov"
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e))
