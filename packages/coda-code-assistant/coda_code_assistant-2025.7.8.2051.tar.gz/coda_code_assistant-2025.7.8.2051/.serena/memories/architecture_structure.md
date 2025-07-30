# Coda Architecture and Structure

## Three-Layer Architecture

```
┌─────────────────────────────────────────────────┐
│                    Apps Layer                    │
│         (CLI, Web UI, Plugins, Custom)          │
├─────────────────────────────────────────────────┤
│                 Services Layer                   │
│    (Integration, Orchestration, Workflows)       │
├─────────────────────────────────────────────────┤
│                   Base Layer                     │
│ (Config, Theme, Providers, Session, Search, etc) │
└─────────────────────────────────────────────────┘
```

## Directory Structure

```
coda/
├── apps/          # User-facing applications
│   ├── cli/       # Command-line interface
│   └── web/       # Web UI (FastAPI/Streamlit)
├── services/      # Business logic
│   ├── agents/    # AI agent implementations
│   ├── tools/     # Tool implementations
│   └── integration/ # External service integrations
└── base/          # Core functionality
    ├── config/    # Configuration management
    ├── providers/ # AI provider implementations
    ├── session/   # Conversation persistence
    ├── search/    # Tree-sitter semantic search
    ├── theme/     # Terminal UI formatting
    └── observability/ # Logging, metrics, tracing
```

## Key Design Patterns
- **Registry Pattern**: Used for providers, agents, and tools
- **Provider Interface**: All AI providers implement common interface
- **Mock Provider**: Special provider for testing with predictable responses
- **Session Management**: XDG-compliant directory structure