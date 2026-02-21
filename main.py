#!/usr/bin/env python3
"""
CodiCode - Local Autonomous Coding Agent
Main entry point for the application.
"""

import sys
import argparse
from src.config import Config
from src.llm import OllamaLLM
from src.tools import get_registry
from src.tools.file_tools import (
    ReadFileTool,
    WriteFileTool,
    ListDirectoryTool,
    FileExistsTool
)
from src.tools.shell_tools import (
    RunShellTool,
    GetWorkingDirectoryTool
)
from src.tools.search_tools import (
    GrepSearchTool,
    FindFilesTool
)
from src.cli import create_cli


def setup_tools(registry):
    """Register all available tools."""
    # File tools
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(ListDirectoryTool())
    registry.register(FileExistsTool())

    # Shell tools
    registry.register(RunShellTool())
    registry.register(GetWorkingDirectoryTool())

    # Search tools
    registry.register(GrepSearchTool())
    registry.register(FindFilesTool())

    print(f"[Setup] Registered {len(registry.list_tools())} tools")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CodiCode - Local Autonomous Coding Agent"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="codellama:7b",
        help="LLM model to use (default: codellama:7b)"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:11434",
        help="Ollama base URL (default: http://localhost:11434)"
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=50,
        help="Maximum agent steps (default: 50)"
    )
    parser.add_argument(
        "--task",
        type=str,
        help="Single task to execute (non-interactive mode)"
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output"
    )

    args = parser.parse_args()

    # Load configuration
    config = Config.default()
    config.llm.model_name = args.model
    config.llm.base_url = args.base_url
    config.agent.max_steps = args.max_steps

    print("[Setup] Initializing CodiCode...")
    print(f"[Setup] LLM: {config.llm.provider} - {config.llm.model_name}")
    print(f"[Setup] Base URL: {config.llm.base_url}")

    # Initialize LLM
    try:
        llm = OllamaLLM(
            model_name=config.llm.model_name,
            base_url=config.llm.base_url
        )
        print("[Setup] LLM initialized")
    except Exception as e:
        print(f"[Error] Failed to initialize LLM: {str(e)}")
        print("[Error] Make sure Ollama is running: ollama serve")
        sys.exit(1)

    # Initialize tool registry
    registry = get_registry()
    setup_tools(registry)

    # Create CLI
    cli = create_cli(llm, registry)

    # Run
    if args.task:
        # Non-interactive mode
        print(f"\n[Task] Executing: {args.task}\n")
        result = cli.run_single_task(args.task)
        print(f"\n[Result]\n{result}")
    else:
        # Interactive mode
        cli.run()


if __name__ == "__main__":
    main()
