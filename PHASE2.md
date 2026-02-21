# Phase 2 Features - Advanced Capabilities

CodiCode Phase 2 adds production-ready features for professional development workflows.

## What's New in Phase 2

### 1. Real Embeddings 🧠

**Sentence Transformers Integration**
- High-quality semantic embeddings for code
- Support for multiple models:
  - `all-MiniLM-L6-v2` - Fast, 384 dimensions
  - `all-mpnet-base-v2` - Better quality, 768 dimensions
  - `microsoft/codebert-base` - Code-specialized model

**Installation:**
```bash
pip install sentence-transformers torch
```

**Usage:**
```python
from src.codebase.embeddings_sentence_transformer import SentenceTransformerEmbedding

# Use sentence transformers
embedder = SentenceTransformerEmbedding("all-MiniLM-L6-v2")
vector = embedder.embed_text("def hello(): print('world')")

# Or use CodeBERT for better code understanding
from src.codebase.embeddings_sentence_transformer import CodeBERTEmbedding
embedder = CodeBERTEmbedding("microsoft/codebert-base")
```

---

### 2. AST-Based Semantic Chunking 🌳

**Smart Code Parsing**
- Extracts functions, classes, methods as semantic units
- Includes docstrings and metadata
- Tracks imports and function calls

**Features:**
- Parse Python files into logical chunks
- Extract metadata (function args, class inheritance, etc.)
- Map function call graphs
- Identify imports and dependencies

**Installation:** No extra deps (uses Python stdlib `ast`)

**Usage:**
```python
from src.codebase.ast_chunker import ASTChunker

chunker = ASTChunker()
chunks = chunker.chunk_file("src/agent/controller.py")

for chunk in chunks:
    print(f"{chunk.metadata['name']} ({chunk.chunk_type})")
    print(f"  Lines: {chunk.start_line}-{chunk.end_line}")
    print(f"  Args: {chunk.metadata.get('args', [])}")
```

**Example Output:**
```
AgentController (class)
  Lines: 15-120
  Methods: ['__init__', 'execute_task', 'reset']

execute_task (function)
  Lines: 35-85
  Args: ['self', 'user_request']
```

---

### 3. FAISS Vector Store 💾

**Persistent Similarity Search**
- Efficient similarity search with FAISS
- Disk persistence (save/load indexes)
- Support for different index types:
  - **Flat** - Exact search (slower, accurate)
  - **IVF** - Approximate search (faster)
  - **HNSW** - Graph-based (fast + accurate)

**Installation:**
```bash
pip install faiss-cpu  # or faiss-gpu for GPU support
```

**Usage:**
```python
from src.codebase.faiss_vectorstore import CodebaseFAISSStore

# Create store
store = CodebaseFAISSStore(dimension=384, index_type="Flat")

# Add code chunks with embeddings
store.add_code_chunk(
    chunk_id="main.py:15-30",
    vector=embedding_vector,
    code="def main(): ...",
    file_path="main.py",
    start_line=15,
    end_line=30
)

# Search similar code
results = store.search(query_vector, top_k=5)
for entry, similarity in results:
    print(f"{entry.metadata['file_path']}:{entry.metadata['start_line']}")
    print(f"  Similarity: {similarity:.3f}")

# Save to disk
store.save("./vectorstore")

# Load later
store.load("./vectorstore")
```

---

### 4. Streaming CLI ⚡

**Real-Time Response Streaming**
- See LLM responses as they're generated
- Better user experience
- Live tool execution feedback

**Usage:**
```bash
python main.py --streaming  # (add to main.py)
```

**Features:**
- Token-by-token streaming
- Visual tool execution indicators
- Progress updates

**Implementation:**
```python
from src.cli.streaming_interface import create_streaming_cli

cli = create_streaming_cli(agent)
cli.run()
```

---

### 5. Git Integration 📦

**Version Control Tools**
- 5 new git tools for the agent:
  - `git_status` - Check repository status
  - `git_diff` - View changes
  - `git_log` - View commit history
  - `git_branch` - List/create branches
  - `git_commit` - Stage and commit

**Usage in Agent:**
```
>>> Check git status and show recent commits
[Agent executes: git_status, git_log]

>>> Create a new branch called feature-x
[Agent executes: git_branch with action=create]

>>> Commit all changes with message "Added feature X"
[Agent executes: git_commit]
```

**Register Tools:**
```python
from src.tools.git_tools import (
    GitStatusTool, GitDiffTool, GitLogTool,
    GitBranchTool, GitCommitTool
)

registry.register(GitStatusTool())
registry.register(GitDiffTool())
registry.register(GitLogTool())
registry.register(GitBranchTool())
registry.register(GitCommitTool())
```

---

### 6. Test & Validation Tools ✅

**Quality Assurance Toolkit**
- 6 new tools for code quality:
  - `run_pytest` - Execute tests
  - `lint_python` - Run flake8
  - `format_python` - Format with black
  - `type_check` - Check types with mypy
  - `security_check` - Scan with bandit
  - `run_coverage` - Measure test coverage

**Installation:**
```bash
pip install pytest black flake8 mypy bandit pytest-cov
```

**Usage:**
```
>>> Run tests in the tests/ directory
[Agent executes: run_pytest]

>>> Lint all Python files and fix formatting
[Agent executes: lint_python, format_python]

>>> Check for security issues
[Agent executes: security_check]

>>> Run tests with coverage
[Agent executes: run_coverage]
```

**Register Tools:**
```python
from src.tools.test_tools import (
    PytestRunTool, PythonLintTool, PythonFormatTool,
    TypeCheckTool, SecurityCheckTool, CodeCoverageTool
)

registry.register(PytestRunTool())
registry.register(PythonLintTool())
registry.register(PythonFormatTool())
registry.register(TypeCheckTool())
registry.register(SecurityCheckTool())
registry.register(CodeCoverageTool())
```

---

## Complete Tool List (Phase 1 + 2)

### File Operations (4)
- read_file
- write_file
- list_directory
- file_exists

### Shell (2)
- run_shell
- get_working_directory

### Search (2)
- grep_search
- find_files

### Git (5) 🆕
- git_status
- git_diff
- git_log
- git_branch
- git_commit

### Testing & QA (6) 🆕
- run_pytest
- lint_python
- format_python
- type_check
- security_check
- run_coverage

**Total: 19 tools**

---

## Installation Guide

### Minimal (Phase 1)
```bash
pip install requests
```

### With Embeddings
```bash
pip install requests sentence-transformers torch
```

### With Vector Store
```bash
pip install requests sentence-transformers torch faiss-cpu
```

### Full Development Setup
```bash
pip install requests sentence-transformers torch faiss-cpu \
  pytest black flake8 mypy bandit pytest-cov
```

---

## Example: Build a Complete Workflow

```python
from src.agent.controller import AgentController
from src.llm.ollama import OllamaLLM
from src.tools import get_registry

# Import Phase 2 tools
from src.tools.git_tools import GitStatusTool, GitCommitTool
from src.tools.test_tools import PytestRunTool, PythonFormatTool

# Setup
llm = OllamaLLM("codellama:7b")
registry = get_registry()

# Register all tools (Phase 1 + Phase 2)
registry.register_all([
    # ... Phase 1 tools ...
    GitStatusTool(),
    GitCommitTool(),
    PytestRunTool(),
    PythonFormatTool()
])

# Create agent
agent = AgentController(llm, registry)

# Execute complex workflow
result = agent.execute_task(
    "Check git status, run tests, format code, and commit if tests pass"
)
```

---

## Benchmarks

### Embedding Performance
| Model | Dimension | Speed | Quality |
|-------|-----------|-------|---------|
| all-MiniLM-L6-v2 | 384 | ⚡⚡⚡ | ★★★☆☆ |
| all-mpnet-base-v2 | 768 | ⚡⚡☆ | ★★★★☆ |
| CodeBERT | 768 | ⚡☆☆ | ★★★★★ |

### FAISS Search Performance
| Index Type | Build Time | Search Time | Accuracy |
|------------|------------|-------------|----------|
| Flat | Fast | Slow | 100% |
| IVF | Slow | Fast | ~95% |
| HNSW | Medium | Very Fast | ~98% |

---

## Migration from Phase 1

Phase 2 is **fully backward compatible**. All Phase 1 code continues to work.

To enable Phase 2 features:

1. **Install optional dependencies**
2. **Import new modules as needed**
3. **Register additional tools**

No changes to existing code required!

---

## Roadmap: Phase 3

Coming soon:
- [ ] Multi-file context management
- [ ] Persistent conversation memory
- [ ] Code review capabilities
- [ ] Web UI interface
- [ ] Multi-agent collaboration
- [ ] llama.cpp and vLLM backends
- [ ] Fine-tuned coding models

---

## Performance Tips

**Embeddings:**
- Use MiniLM for speed
- Use CodeBERT for accuracy
- Batch process large codebases

**Vector Store:**
- Use Flat for <10K vectors
- Use IVF for >10K vectors
- Use HNSW for read-heavy workloads

**Testing:**
- Run tests in parallel: `pytest -n auto`
- Use coverage caching
- Skip slow tests in CI

---

**Phase 2 Complete! 🎉**

You now have a production-ready autonomous coding agent with enterprise features.
