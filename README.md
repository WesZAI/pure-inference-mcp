# Pure Inference MCP (No-Agent Architecture) 🚀

This repository demonstrates how to build a lightning-fast, token-saving AI development environment using the **Model Context Protocol (MCP)** and a single local Python server. 

**Zero Agents. Zero JSON bloating. Zero RAG fluff. Just pure inference and direct tools.**

## The Philosophy
Why hide pure AI intelligence behind layers of rigid agent frameworks, loops, and vector databases? A modern LLM only needs two things:
1. **Eyes and Hands:** Native tools provided directly via a local MCP server.
2. **A Single Source of Truth:** A highly dense, auto-compressed `AI.md` file that acts as the live memory.

By clearing the chat history after each sync, you keep your context clean, completely avoid "copy of a copy" prompt bloat, and protect your API budget.

## File Structure
- `main.py` -> The lightweight local MCP server exposing native tools.
- `AI.md` -> The compressed project memory (read and updated directly by the LLM).

## Quick Start

1. Install dependencies:
```bash
pip install mcp
```

2. Run the server (or connect it directly to your VS Code / Claude / Gemini configuration):
```bash
python main.py
```

## The Workflow
1. **Load Context:** The LLM uses `read_memory` to instantly internalize the project state from `AI.md`.
2. **Work:** Code directly with the LLM.
3. **Save & Compress:** Before closing the chat, the LLM calls `update_memory` to write a dense, hyper-focused summary back into `AI.md`.
4. **Purge:** Clear the chat window. Your context is fresh, your token usage drops back to near-zero.