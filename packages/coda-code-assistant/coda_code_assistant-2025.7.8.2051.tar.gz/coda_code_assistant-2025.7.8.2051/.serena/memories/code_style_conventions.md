# Code Style and Conventions

## General Style
- **Python Version**: 3.11+ (uses modern Python features)
- **Formatter**: Black with line length 100
- **Linter**: Ruff with specific rules (E, F, W, I, N, B, UP)
- **Style Guide**: PEP 8 compliant

## Code Conventions
- **Type Hints**: Required for all functions and methods
- **Docstrings**: Required for all public APIs, modules, classes, and functions
- **Imports**: Organized and sorted by ruff
- **Naming**: 
  - Functions/variables: snake_case
  - Classes: PascalCase
  - Constants: UPPER_SNAKE_CASE
  - Private methods/attributes: prefix with underscore

## File Organization
- Module docstrings at the top explaining purpose
- Imports organized in standard order
- Functions should be focused and small
- Classes follow single responsibility principle

## Testing Conventions
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`
- Use pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.functional`
- Mock external services in unit tests
- Use mock provider for predictable AI responses

## Version Format
- Date-based: `year.month.day.HHMM`
- Example: `2025.7.8.2051`
- Automatically updated via `update_version.py`

## Commit Conventions
- Use Conventional Commits format
- Types: feat, fix, perf, refactor, docs, style, test, chore
- Examples:
  - `feat(cli): add interactive mode`
  - `fix(oci): handle auth timeout`
  - `docs: update README`