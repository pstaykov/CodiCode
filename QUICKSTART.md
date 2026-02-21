# Quick Start Guide

Get CodiCode running in 5 minutes.

## Step 1: Install Ollama

```bash
# Linux/Mac
curl -fsSL https://ollama.ai/install.sh | sh

# Or visit: https://ollama.ai/download
```

## Step 2: Start Ollama & Pull a Model

```bash
# Start Ollama server (keep this running)
ollama serve

# In another terminal, pull a coding model
ollama pull codellama:7b

# Alternative models:
# ollama pull deepseek-coder:6.7b
# ollama pull codellama:13b
```

## Step 3: Install CodiCode

```bash
# Clone and setup
cd CodiCode
pip install -r requirements.txt
```

## Step 4: Run Your First Task

```bash
# Interactive mode
python main.py

# Try these commands:
>>> help
>>> tools
>>> Read the file README.md and summarize it
>>> quit
```

## Step 5: Try Non-Interactive Mode

```bash
# Single task execution
python main.py --task "List all Python files in the src directory"

# With custom model
python main.py --model deepseek-coder:6.7b --task "Find all TODO comments"
```

## Example Tasks to Try

1. **File Operations**
   ```
   Read the file main.py and explain what it does
   ```

2. **Search**
   ```
   Find all files with 'agent' in the name
   ```

3. **Code Analysis**
   ```
   Search for all function definitions in src/agent/
   ```

4. **Multi-step Tasks**
   ```
   List all Python files, then read the controller.py file
   ```

## Troubleshooting

### "Connection refused" error
- Make sure Ollama is running: `ollama serve`
- Check it's on the right port: `curl http://localhost:11434`

### Model not found
- Pull the model first: `ollama pull codellama:7b`
- List available models: `ollama list`

### Python import errors
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (needs 3.8+)

## Next Steps

- Read the [full README](README.md) for architecture details
- Explore the code in `src/` to understand the system
- Try extending with custom tools
- Check out the roadmap for future features

## Tips

- Use `status` command to see agent state
- Use `reset` to clear conversation history
- Press Ctrl+C to interrupt long-running tasks
- Tool execution is logged for debugging

---

**You're ready to code with AI! 🚀**
