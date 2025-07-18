# 🔄 Migration Guide

## Overview

This guide helps you understand the changes made to the project structure and how to update your usage patterns.

## What Changed

### File Movements

| Old Location | New Location | Purpose |
|-------------|-------------|---------|
| `cli.py` | `scripts/cli.py` | Command-line interface |
| `debug_email.py` | `scripts/debug_email.py` | Email debugging |
| `test_pipeline.py` | `scripts/test_pipeline.py` | Pipeline testing |
| `troubleshoot.py` | `scripts/troubleshoot.py` | System diagnostics |
| `QUICK_START.md` | `docs/QUICK_START.md` | Quick start guide |
| `README.md` | `docs/README.md` (full docs) | Comprehensive docs |

### New Folder Structure

```
AI-Agents-Swarm/
├── agents/         # Core functionality (unchanged)
├── scripts/        # 🆕 All utility scripts
├── docs/          # 🆕 All documentation
├── tests/         # 🆕 Test suites
├── tools/         # 🆕 Development tools
├── ui/            # User interfaces (unchanged)
├── api/           # REST API (unchanged)
└── config/        # Configuration (unchanged)
```

## Updated Commands

### Before (Old Commands)
```bash
# Old ways to run scripts
python cli.py run
python debug_email.py
python test_pipeline.py
python troubleshoot.py
```

### After (New Commands)
```bash
# New ways to run scripts
python scripts/cli.py run
python scripts/debug_email.py
python scripts/test_pipeline.py
python scripts/troubleshoot.py
```

## Path Updates

### Import Paths
Scripts now use updated import paths:

```python
# Old (from root)
from agents.core import BaseAgent

# New (from scripts/)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
from agents.core import BaseAgent
```

### Documentation References
Updated documentation links:

```markdown
# Old
[Quick Start](QUICK_START.md)

# New
[Quick Start](docs/QUICK_START.md)
```

## Benefits of New Structure

### 🎯 Clean Root Directory
- Only essential files in root
- Clear separation of concerns
- Professional project appearance

### 🚀 Better Organization
- All scripts in `scripts/` folder
- All documentation in `docs/` folder
- Related files grouped together

### 🔍 Easier Navigation
- Know exactly where to find files
- Logical grouping by purpose
- Reduced clutter in root

## Migration Steps

### If You Have Local Changes

1. **Check your current scripts**:
   ```bash
   # See what files you have
   ls -la *.py
   ```

2. **Update your commands**:
   ```bash
   # Change from:
   python cli.py dashboard
   
   # To:
   python scripts/cli.py dashboard
   ```

3. **Update any custom scripts**:
   ```python
   # Update import paths in your scripts
   import sys
   from pathlib import Path
   
   project_root = Path(__file__).parent.parent
   sys.path.insert(0, str(project_root))
   ```

### If You're Starting Fresh

1. **Follow the new README**:
   ```bash
   # Use the new commands
   python scripts/cli.py run
   python scripts/troubleshoot.py
   ```

2. **Check documentation**:
   ```bash
   # Documentation is now in docs/
   cat docs/QUICK_START.md
   ```

## Quick Reference

### Most Common Commands
```bash
# System diagnostics
python scripts/troubleshoot.py

# Run the CLI
python scripts/cli.py run

# Launch dashboard
python scripts/cli.py dashboard

# Test pipeline
python scripts/test_pipeline.py

# Debug email processing
python scripts/debug_email.py
```

### File Locations
- **Scripts**: `scripts/` folder
- **Documentation**: `docs/` folder
- **Tests**: `tests/` folder
- **Configuration**: `config/` folder (unchanged)
- **Core agents**: `agents/` folder (unchanged)

## Need Help?

If you encounter issues with the new structure:

1. **Check the troubleshoot script**:
   ```bash
   python scripts/troubleshoot.py
   ```

2. **Review the project structure**:
   ```bash
   # See the new organization
   tree /f  # Windows
   # or
   find . -type f -name "*.py" | head -20  # Linux/Mac
   ```

3. **Check the documentation**:
   - [Project Structure](docs/PROJECT_STRUCTURE.md)
   - [Quick Start](docs/QUICK_START.md)
   - [Full Documentation](docs/README.md)

The new structure is designed to be more maintainable and professional while keeping all the same functionality you're used to!
