# Coda Project Overview

## Purpose
Coda is a powerful, modular AI code assistant that brings AI-powered development directly to your terminal. It supports multiple AI providers including Oracle OCI GenAI, OpenAI, Anthropic, Google, and 100+ more via LiteLLM.

## Tech Stack
- **Language**: Python 3.11+
- **Package Manager**: uv (required, not pip)
- **AI Integration**: litellm for multi-provider support
- **Terminal UI**: rich, prompt-toolkit, pygments
- **Code Intelligence**: tree-sitter, grep-ast
- **Testing**: pytest with comprehensive test suite
- **Formatting**: black (line length 100)
- **Linting**: ruff
- **Type Checking**: mypy (optional)

## Key Features
- Multi-provider AI support (Oracle OCI GenAI, OpenAI, Anthropic, Google, Ollama, 100+ via LiteLLM)
- Modular architecture allowing use of individual components
- Terminal-first design for CLI developers
- Smart AI modes for specialized tasks
- Session management for conversation persistence
- Semantic code search capabilities
- Rich terminal UI with syntax highlighting
- Tool integration via MCP
- Comprehensive test coverage

## Development Platform
System: Darwin (macOS)