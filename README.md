# CodiCode

A fully local, autonomous coding agent with a clean architecture similar to Claude Code. Built for running completely offline with local LLMs.

## Features

✅ **Fully Local** - No API keys, no cloud dependencies
✅ **Autonomous Agent Loop** - Multi-step planning and execution
✅ **Tool System** - Extensible tool registry with file, shell, and search tools
✅ **Diff Engine** - Safe file modifications with preview and rollback
✅ **CLI Interface** - Interactive terminal with colored output
✅ **Pluggable LLM Backend** - Support for Ollama, llama.cpp, vLLM
✅ **Codebase Intelligence** - Chunking and embedding system (Phase 1 implemented)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Interface                         │
│                   (Interactive Terminal)                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Agent Controller                          │
│         (Autonomous Loop: Plan → Act → Observe)             │
└─────────┬───────────────────────────────────────────┬───────┘
          │                                           │
┌─────────▼────────┐                      ┌──────────▼────────┐
│     Planner      │                      │   Tool Registry    │
│  (Task Planning) │                      │ (Tool Execution)   │
└──────────────────┘                      └──────────┬─────────┘
                                                     │
                          ┌──────────────────────────┼──────────────────────┐
                          │                          │                      │
                  ┌───────▼────────┐      ┌─────────▼────────┐  ┌─────────▼────────┐
                  │   File Tools   │      │   Shell Tools    │  │  Search Tools    │
                  │ read/write/ls  │      │   run_shell      │  │  grep/find       │
                  └────────────────┘      └──────────────────┘  └──────────────────┘
                          │
                  ┌───────▼────────┐
                  │  Diff Engine   │
                  │ (Safe Patches) │
                  └────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    LLM Abstraction Layer                     │
│              (Ollama / llama.cpp / vLLM)                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Codebase Intelligence (Phase 1)                 │
│         Chunker → Embeddings (stub) → VectorStore           │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
CodiCode/
├── src/
│   ├── agent/
│   │   ├── controller.py       # Main agent loop
│   │   └── planner.py          # Task planning
│   ├── llm/
│   │   ├── base.py             # LLM interface
│   │   └── ollama.py           # Ollama backend
│   ├── tools/
│   │   ├── registry.py         # Tool management
│   │   ├── file_tools.py       # File operations
│   │   ├── shell_tools.py      # Shell commands
│   │   └── search_tools.py     # Search operations
│   ├── diff/
│   │   └── engine.py           # Diff/patch system
│   ├── codebase/
│   │   ├── chunker.py          # Code chunking
│   │   ├── embeddings.py       # Embedding interface
│   │   └── vectorstore.py      # Vector storage
│   ├── cli/
│   │   ├── interface.py        # CLI logic
│   │   └── display.py          # Output formatting
│   └── config.py               # Configuration
├── main.py                     # Entry point
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites

1. **Python 3.8+**
2. **Ollama** (for local LLM)
   ```bash
   # Install Ollama: https://ollama.ai
   curl -fsSL https://ollama.ai/install.sh | sh

   # Pull a coding model
   ollama pull codellama:7b
   # or
   ollama pull deepseek-coder:6.7b
   ```

### Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd CodiCode

# Install dependencies
pip install -r requirements.txt

# Make main.py executable (optional)
chmod +x main.py
```

## Usage

### Interactive Mode

```bash
# Start Ollama (in a separate terminal)
ollama serve

# Run CodiCode
python main.py

# Or with custom model
python main.py --model deepseek-coder:6.7b
```

**Example session:**
```
CodiCode - Local Autonomous Coding Agent
ℹ Type your request or 'quit' to exit
ℹ Type 'help' for available commands

>>> Read the file main.py and summarize its purpose

[Agent] Starting task: Read the file main.py and summarize its purpose
[Agent] Step 1/50
🔧 Calling tool: read_file
   Arguments: {'path': 'main.py'}
✓ Tool result: Successfully read file...

[Agent] Step 2/50
Task complete

Result:
The main.py file is the entry point for CodiCode, an autonomous coding agent...
```

### Non-Interactive Mode

```bash
# Execute a single task
python main.py --task "Find all Python files in src/"

# With custom settings
python main.py \
  --model codellama:7b \
  --max-steps 100 \
  --task "Analyze the agent controller code"
```

### Available Commands

In interactive mode:

- `help` - Show help message
- `quit` / `exit` - Exit the application
- `reset` - Reset agent state
- `status` - Show agent status
- `tools` - List available tools

## Available Tools

### File Tools
- **read_file** - Read file contents
- **write_file** - Write content to a file
- **list_directory** - List directory contents
- **file_exists** - Check if a path exists

### Shell Tools
- **run_shell** - Execute shell commands (with safety checks)
- **get_working_directory** - Get current working directory

### Search Tools
- **grep_search** - Search for patterns in files
- **find_files** - Find files by name pattern

## Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# LLM Configuration
LLM_PROVIDER=ollama
LLM_MODEL=codellama:7b
LLM_BASE_URL=http://localhost:11434
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096

# Agent Configuration
AGENT_MAX_STEPS=50
AGENT_MAX_ERRORS=5
AGENT_REQUIRE_APPROVAL=true
AGENT_VERBOSE=true

# Codebase Intelligence
CHUNK_SIZE=100
CHUNK_OVERLAP=20
EMBEDDING_PROVIDER=stub
ENABLE_VECTORSTORE=false
```

### Command-Line Arguments

```bash
python main.py --help

usage: main.py [-h] [--model MODEL] [--base-url BASE_URL]
               [--max-steps MAX_STEPS] [--task TASK] [--no-color]

Options:
  --model MODEL         LLM model to use
  --base-url BASE_URL   Ollama base URL
  --max-steps N         Maximum agent steps
  --task TASK           Single task (non-interactive)
  --no-color            Disable colored output
```

## Extending CodiCode

### Adding a New Tool

1. Create a tool class inheriting from `BaseTool`:

```python
from src.tools.base import BaseTool, ToolResult

class MyCustomTool(BaseTool):
    @property
    def name(self) -> str:
        return "my_tool"

    @property
    def description(self) -> str:
        return "Description of what my tool does"

    @property
    def parameters_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "..."}
            },
            "required": ["param1"]
        }

    def execute(self, param1: str) -> ToolResult:
        # Tool implementation
        return ToolResult(success=True, data="result")
```

2. Register it in `main.py`:

```python
from src.tools.my_tool import MyCustomTool

def setup_tools(registry):
    # ... existing tools ...
    registry.register(MyCustomTool())
```

### Adding a New LLM Backend

1. Implement `BaseLLM` interface:

```python
from src.llm.base import BaseLLM, Message, LLMResponse

class MyLLMBackend(BaseLLM):
    def generate(self, messages, tools=None, **kwargs) -> LLMResponse:
        # Implementation
        pass

    def generate_stream(self, messages, tools=None, **kwargs):
        # Implementation
        pass
```

2. Update `main.py` to use your backend.

## Safety Features

- **Command validation** - Dangerous shell commands are blocked
- **Backup system** - Files are backed up before modification
- **Diff preview** - See changes before they're applied
- **Step limits** - Prevents infinite loops
- **Error tracking** - Aborts after too many tool errors

## Limitations

- Phase 1 uses stub embeddings (hash-based)
- No persistent storage yet
- Limited context window management
- Basic planning heuristics

## Contributing

Contributions welcome! Focus areas:

1. Additional tool implementations
2. LLM backend adapters
3. Better planning strategies
4. Real embedding integration
5. Documentation improvements

## License

MIT License - See LICENSE file for details

## Acknowledgments

Inspired by:
- Claude Code (Anthropic)

Built with clean architecture principles and no heavy frameworks.

---

**Built by me for local-first AI coding.**
