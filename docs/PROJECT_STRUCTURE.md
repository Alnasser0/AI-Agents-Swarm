# 📁 Project Structure

## Overview

The AI Agents Swarm project is organized into logical folders to maintain clean separation of concerns and easy navigation.

## Directory Structure

```
AI-Agents-Swarm/
├── 📁 agents/                  # Core agent functionality
│   ├── core/                   # Base classes and shared utilities
│   ├── email_polling/          # Email processing agents
│   ├── notion_integration/     # Notion API integration
│   ├── slack_integration/      # Slack integration (future)
│   └── main.py                 # Main orchestrator
│
├── 📁 api/                     # REST API server
│   ├── routes/                 # API route definitions
│   ├── models/                 # API data models
│   └── server.py               # FastAPI server
│
├── 📁 config/                  # Configuration management
│   ├── settings.py             # Application settings
│   └── __init__.py             # Configuration exports
│
├── 📁 ui/                      # User interfaces
│   ├── dashboard.py            # Streamlit dashboard
│   ├── components/             # UI components
│   └── static/                 # Static assets
│
├── 📁 scripts/                 # Utility scripts and tools
│   ├── cli.py                  # Command-line interface
│   ├── debug_email.py          # Email debugging script
│   ├── test_pipeline.py        # Pipeline testing script
│   ├── troubleshoot.py         # System troubleshooting
│   └── cleanup.py              # File cleanup utility
│
├── 📁 docs/                    # Documentation
│   ├── README.md               # Comprehensive documentation
│   ├── QUICK_START.md          # Quick start guide
│   ├── api.md                  # API documentation
│   └── deployment.md           # Deployment guide
│
├── 📁 tests/                   # Test suites
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── conftest.py             # Test configuration
│
├── 📁 tools/                   # Development tools
│   ├── linting/                # Code quality tools
│   ├── formatting/             # Code formatting
│   └── ci/                     # CI/CD scripts
│
├── 📁 data/                    # Data storage
│   ├── processed_emails.pkl    # Processed email tracking
│   ├── cache/                  # Temporary cache files
│   └── backups/                # Data backups
│
├── 📁 logs/                    # Application logs
│   ├── agents.log              # Main application log
│   ├── errors.log              # Error logs
│   └── archived/               # Archived logs
│
├── 📁 examples/                # Example scripts and demos
│   ├── basic_usage.py          # Basic usage examples
│   ├── custom_agents.py        # Custom agent examples
│   └── integration_examples/   # Integration examples
│
├── 📁 utils/                   # Shared utility functions
│   ├── email_utils.py          # Email utilities
│   ├── notion_utils.py         # Notion utilities
│   └── ai_utils.py             # AI helper functions
│
└── 📄 Root Files               # Essential project files
    ├── README.md               # Main project documentation
    ├── requirements.txt        # Python dependencies
    ├── setup.py               # Installation script
    ├── .env.example           # Environment template
    ├── .gitignore             # Git ignore rules
    ├── docker-compose.yml     # Docker configuration
    ├── Dockerfile             # Container definition
    └── LICENSE                # License file
```

## Folder Purposes

### 🤖 `agents/`
Contains all agent implementations and core functionality:
- **`core/`**: Base classes, shared utilities, and common functionality
- **`email_polling/`**: Email monitoring and processing logic
- **`notion_integration/`**: Notion API integration and task creation
- **`slack_integration/`**: Slack integration (placeholder for future)
- **`main.py`**: Main orchestrator that coordinates all agents

### 🌐 `api/`
REST API server implementation:
- **`routes/`**: API endpoint definitions
- **`models/`**: Request/response data models
- **`server.py`**: FastAPI application server

### ⚙️ `config/`
Configuration management:
- **`settings.py`**: Application settings and environment variables
- Centralized configuration for all components

### 🎨 `ui/`
User interface components:
- **`dashboard.py`**: Main Streamlit dashboard
- **`components/`**: Reusable UI components
- **`static/`**: Static assets (CSS, images, etc.)

### 🔧 `scripts/`
Utility scripts and command-line tools:
- **`cli.py`**: Main command-line interface
- **`debug_email.py`**: Email processing debugging
- **`test_pipeline.py`**: Pipeline testing
- **`troubleshoot.py`**: System diagnostics
- **`cleanup.py`**: File organization utilities

### 📚 `docs/`
Comprehensive documentation:
- **`README.md`**: Full project documentation
- **`QUICK_START.md`**: Quick start guide
- **`api.md`**: API documentation
- **`deployment.md`**: Deployment guide

### 🧪 `tests/`
Test suites and testing utilities:
- **`unit/`**: Unit tests for individual components
- **`integration/`**: Integration tests for workflows
- **`conftest.py`**: Test configuration and fixtures

### 🛠️ `tools/`
Development tools and utilities:
- **`linting/`**: Code quality tools
- **`formatting/`**: Code formatting configuration
- **`ci/`**: CI/CD scripts and configuration

### 💾 `data/`
Data storage and persistence:
- **`processed_emails.pkl`**: Tracking of processed emails
- **`cache/`**: Temporary cache files
- **`backups/`**: Data backups

### 📜 `logs/`
Application logging:
- **`agents.log`**: Main application log
- **`errors.log`**: Error-specific logs
- **`archived/`**: Archived log files

### 📖 `examples/`
Example scripts and demonstrations:
- **`basic_usage.py`**: Basic usage examples
- **`custom_agents.py`**: Custom agent examples
- **`integration_examples/`**: Integration examples

### 🔧 `utils/`
Shared utility functions:
- **`email_utils.py`**: Email-related utilities
- **`notion_utils.py`**: Notion-related utilities
- **`ai_utils.py`**: AI helper functions

## Benefits of This Organization

### 🎯 Clear Separation of Concerns
- Each folder has a single, well-defined purpose
- Related functionality is grouped together
- Easy to locate specific types of files

### 🚀 Developer Productivity
- Minimal file hopping between related components
- Logical grouping reduces cognitive load
- Clear naming conventions

### 🔄 Scalability
- Easy to add new agents in the `agents/` folder
- Scripts can be added to `scripts/` without cluttering root
- Documentation stays organized in `docs/`

### 🛡️ Maintainability
- Clear boundaries between components
- Easier to understand project structure
- Reduced coupling between modules

## Usage Guidelines

### Adding New Components

1. **New Agent**: Create in `agents/new_agent/`
2. **New Script**: Add to `scripts/`
3. **New Documentation**: Add to `docs/`
4. **New Test**: Add to `tests/unit/` or `tests/integration/`

### File Naming Conventions

- Use lowercase with underscores: `email_utils.py`
- Be descriptive: `debug_email.py` vs `debug.py`
- Group related files in folders

### Import Paths

With the new structure, imports should be:
```python
# From scripts/
from agents.core import BaseAgent
from config.settings import settings

# From agents/
from agents.email_polling import EmailAgent
from utils.email_utils import parse_email
```

This organization makes the project more professional, maintainable, and easier to navigate for both development and deployment.
