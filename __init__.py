"""
AI Agents Swarm - A minimalist AI automation system for solo developers.

This package provides a complete AI automation system that can:
- Monitor email inboxes for task requests
- Extract task information using AI
- Create tasks in Notion automatically
- Provide dashboard and API interfaces

Key Components:
- agents.core: Base classes and utilities
- agents.email_polling: Email monitoring and processing
- agents.notion_integration: Notion API integration
- agents.main: Application orchestrator
- ui.dashboard: Streamlit dashboard
- api.server: FastAPI REST API

Quick Start:
1. Install dependencies: pip install -r requirements.txt
2. Set up environment: cp .env.example .env (edit with your keys)
3. Run setup: python setup.py
4. Start system: python -m agents.main

For more information, see README.md and QUICK_START.md
"""

__version__ = "1.0.0"
__author__ = "AI Agents Swarm"
__description__ = "Minimalist AI automation system for solo developers"

# Import main components for easy access
from agents.core import BaseAgent, Task, TaskPriority, TaskStatus
from agents.main import AgentOrchestrator

__all__ = [
    "BaseAgent",
    "Task", 
    "TaskPriority",
    "TaskStatus",
    "AgentOrchestrator",
    "__version__",
    "__author__",
    "__description__"
]
