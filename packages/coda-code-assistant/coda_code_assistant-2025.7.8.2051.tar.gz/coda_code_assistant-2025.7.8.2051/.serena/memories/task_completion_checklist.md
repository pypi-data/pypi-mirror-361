# Task Completion Checklist

When completing any coding task in the Coda project, follow these steps:

## 1. Code Quality Checks
```bash
# Format code (REQUIRED)
make format

# Run linters (REQUIRED)
make lint

# Type checking (OPTIONAL but recommended)
make typecheck
```

## 2. Run Tests
```bash
# At minimum, run unit tests
make test

# For more thorough testing
make test-all  # Includes integration tests

# If you modified specific areas, run relevant tests
pytest tests/path/to/relevant/test.py -xvs
```

## 3. Update Version (if releasing)
```bash
# Only if making a release
make version
```

## 4. Documentation
- Update docstrings for new/modified functions
- Update README.md for user-facing changes
- Update CLAUDE.md or AGENTS.md if AI behavior changes

## 5. Before Committing
```bash
# Quick pre-commit check
make pre-commit
# This runs: format + lint + test-fast
```

## 6. Commit Message
- Use Conventional Commits format
- Be clear and descriptive
- Reference issues if applicable

## Important Notes
- NEVER commit without running format and lint
- ALWAYS ensure tests pass before committing
- If lint/typecheck commands are not found, ask user for correct commands
- Consider writing commands to CLAUDE.md for future reference