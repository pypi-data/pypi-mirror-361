# Suggested Development Commands

## Essential Setup
```bash
# Install dependencies (requires uv)
make install-dev
# or
uv sync --all-extras

# Activate virtual environment
source .venv/bin/activate
```

## Development Workflow
```bash
# Format code before committing
make format

# Run linters
make lint

# Run type checking (optional)
make typecheck

# Run all quality checks
make quality  # Runs format + lint + typecheck

# Quick pre-commit checks
make pre-commit  # Runs format + lint + test-fast
```

## Testing Commands
```bash
# Run unit tests only (fast, default)
make test

# Run all tests including integration
make test-all

# Run specific test levels
make test-unit
make test-integration
make test-functional

# Run with coverage
make test-coverage

# Run a single test
pytest tests/path/to/test_file.py::test_function_name -xvs

# Run LLM tests (requires Ollama)
make test-llm
```

## Version Management
```bash
# Update version to current timestamp
make version
# or
./scripts/update_version.py
```

## Running Coda
```bash
# Run CLI
coda --help
coda --version

# Interactive mode
uv run coda
```

## Docker Commands
```bash
# Build Docker image
make docker-build

# Run in Docker
make docker-run

# Development container
make docker-dev
```

## macOS/Darwin Specific Commands
- Standard Unix commands work (ls, cd, grep, find)
- Use `rg` (ripgrep) instead of grep when available
- Git commands function normally