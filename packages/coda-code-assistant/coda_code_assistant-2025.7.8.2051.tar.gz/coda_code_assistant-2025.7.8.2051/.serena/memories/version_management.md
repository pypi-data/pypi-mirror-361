# Version Management in Coda

## Version Format
Coda uses date-based versioning: `year.month.day.HHMM`
- Example: `2025.7.8.2051` (July 8, 2025 at 20:51 UTC)
- Build number is hour and minute in 24-hour format

## Version Files
- **Main version file**: `coda/__version__.py`
- Contains `__version__` variable that is auto-updated
- Includes helper functions for version management

## Updating Version

### Method 1: Make command
```bash
make version
```

### Method 2: Python script
```bash
python scripts/update_version.py
# or
uv run python scripts/update_version.py
```

### Method 3: Direct import
```python
from coda.__version__ import update_version
new_version = update_version()
```

## Version Access
```bash
# CLI command
coda --version

# In Python
from coda.__version__ import __version__
```

## Important Notes
- Version is based on UTC time
- Version updates modify `coda/__version__.py` directly
- No need for manual version bumping
- Version format ensures chronological ordering
- The update script has logic to find and replace the version string