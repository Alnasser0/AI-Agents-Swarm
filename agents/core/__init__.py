"""
Core utilities and base classes for AI Agents Swarm.

This module provides shared functionality across all agents including:
- Base agent classes
- Common AI model configurations
- Logging utilities
- Error handling patterns
"""

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from loguru import logger
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    """Task status options."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class Task(BaseModel):
    """
    Universal task model used across all integrations.
    
    This provides a common interface for tasks regardless of where
    they come from (email, Slack, etc.) or where they go (Notion, Jira, etc.).
    """
    title: str = Field(description="Task title")
    description: str = Field(description="Detailed task description")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Task status")
    source: str = Field(description="Where the task came from (email, slack, etc.)")
    source_id: Optional[str] = Field(default=None, description="Original source identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Task creation timestamp")
    due_date: Optional[datetime] = Field(default=None, description="Task due date")
    tags: List[str] = Field(default_factory=list, description="Task tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional task metadata")


class BaseAgent:
    """
    Base agent class providing common functionality.
    
    All agents should inherit from this class to ensure consistent
    behavior and logging across the system.
    """
    
    def __init__(self, name: str, model: Optional[str] = None):
        """
        Initialize the base agent.
        
        Args:
            name: Agent name for logging
            model: AI model to use. If None, uses the best available model.
        """
        self.name = name
        self.model = model or get_best_available_model()
        self.logger = logger.bind(agent=name)
        self.logger.info(f"Initialized {name} agent with model {self.model}")
    
    def log_task_processed(self, task: Task) -> None:
        """Log when a task is processed."""
        self.logger.info(f"Processed task: {task.title}", extra={"task_id": task.source_id})
    
    def log_error(self, error: Exception, context: str = "") -> None:
        """Log an error with context."""
        self.logger.error(f"Error in {self.name}: {error}", extra={"context": context})


class EmailTaskExtractor(BaseModel):
    """
    Structured output for email task extraction.
    
    This model defines what information should be extracted
    from emails to create proper tasks.
    """
    is_task: bool = Field(description="Whether this email contains a task request")
    title: str = Field(description="Task title extracted from email")
    description: str = Field(description="Detailed description of the task")
    priority: TaskPriority = Field(description="Estimated task priority")
    due_date: Optional[str] = Field(description="Due date if mentioned (YYYY-MM-DD format or natural language like 'March 5th', 'next Friday')")
    tags: List[str] = Field(description="Relevant tags for the task")
    confidence: float = Field(description="Confidence score (0-1) that this is a task", ge=0, le=1)


def create_task_extraction_agent(model: Optional[str] = None) -> Agent[Any, EmailTaskExtractor]:
    """
    Create an AI agent specialized in extracting tasks from text.
    
    This agent is used across different integrations to identify
    and extract task information from various sources.
    Supports multiple AI providers:
    - OpenAI
    - Anthropic
    - Google Gemini

    Args:
        model: AI model to use for task extraction. If None, uses best available model.
        
    Returns:
        Configured Pydantic AI agent
    """
    # Use the best available model if none specified
    if model is None:
        model = get_best_available_model()
    
    return Agent(
        model=model,
        output_type=EmailTaskExtractor,
        system_prompt="""
        You are a task extraction specialist. Your job is to analyze text and determine if it contains a GENUINE HUMAN-TO-HUMAN TASK REQUEST.

        ONLY EXTRACT TASKS THAT ARE:
        - Direct requests from one person to another person
        - Clear work assignments with specific actions
        - Project-related tasks with deliverables
        - Action items from meetings or collaborative discussions

        NEVER EXTRACT TASKS FROM:
        - Security alerts or notifications
        - Automated system messages
        - Marketing emails or newsletters
        - Account notifications or warnings
        - Software updates or maintenance notices
        - Spam or promotional content
        - General information sharing without specific actions

        GENUINE TASK INDICATORS:
        - Personal communication tone ("Hey [Name]", "Hi [Name]", "Dear [Name]")
        - Specific work requests ("Can you create...", "Please work on...", "I need you to...")
        - Project context ("for the [project]", "deadline is [date]", "client needs...")
        - Clear deliverables ("design the page", "write the report", "fix the bug")
        - Personal responsibility assignment ("assigned to you", "your task", "can you handle...")

        AUTOMATIC REJECTIONS:
        - If sender is automated/system (like "security@", "noreply@", "notifications@")
        - If content is generic/templated
        - If it's about account security, alerts, or system notifications
        - If it's promotional or marketing content
        - If no specific person is being asked to do something

        CONFIDENCE SCORING:
        - 0.9+: Clear personal task request between humans
        - 0.7-0.9: Likely personal task but needs verification
        - 0.5-0.7: Ambiguous - could be task or just information
        - 0.3-0.5: Unlikely to be a genuine task
        - 0.3-: Definitely not a task (automated, promotional, etc.)

        BE EXTREMELY CONSERVATIVE - Only extract tasks you're absolutely confident are genuine human-to-human work requests.
        """
    )


def get_available_models() -> Dict[str, List[str]]:
    """
    Get a dictionary of available AI models by provider.
    
    Returns:
        Dictionary mapping provider names to lists of model names
    """
    return {
        "openai": [
            "openai:gpt-4o",
            "openai:gpt-4o-mini",
            "openai:gpt-4-turbo",
            "openai:gpt-3.5-turbo"
        ],
        "anthropic": [
            "anthropic:claude-3-5-sonnet-latest",
            "anthropic:claude-3-5-haiku-latest",
            "anthropic:claude-3-opus-latest"
        ],
        "google": [
            "google-gla:gemini-2.5-pro",
            "google-gla:gemini-2.5-flash",
            "google-gla:gemini-2.0-flash",
            "google-gla:gemini-2.0-flash-lite",
            "google-vertex:gemini-2.5-pro",
            "google-vertex:gemini-2.5-flash",
            "google-vertex:gemini-2.0-flash",
        ]
    }


def validate_model_availability(model: str) -> bool:
    """
    Validate if a model is available and properly configured.
    
    Args:
        model: Model identifier (e.g., "openai:gpt-4o")
        
    Returns:
        True if model is available and configured
    """
    from config.settings import settings
    
    # Check if required API keys are configured
    if model.startswith("openai:"):
        return bool(settings.openai_api_key and settings.openai_api_key != "your-openai-api-key")
    elif model.startswith("anthropic:"):
        return bool(settings.anthropic_api_key and settings.anthropic_api_key != "your-anthropic-api-key")
    elif model.startswith("google:") or model.startswith("google-gla:") or model.startswith("google-vertex:"):
        return bool((settings.gemini_api_key and settings.gemini_api_key != "your-gemini-api-key") or
                   (settings.google_api_key and settings.google_api_key != "your-google-api-key"))
    
    return False


def get_best_available_model() -> str:
    """
    Get the best available AI model based on configured API keys.
    
    Returns:
        Best available model identifier
    """
    from config.settings import settings
    
    # Priority order: Google Gemini 2.5 Pro > Gemini 2.5 Flash > Anthropic > OpenAI
    # Check if we have valid API keys (not placeholder values)
    if (settings.google_api_key and settings.google_api_key != "your-google-api-key") or \
       (settings.gemini_api_key and settings.gemini_api_key != "your-gemini-api-key"):
        return "google-gla:gemini-2.0-flash-lite" # default
    elif settings.anthropic_api_key and settings.anthropic_api_key != "your-anthropic-api-key":
        return "anthropic:claude-3-5-sonnet-latest"
    elif settings.openai_api_key and settings.openai_api_key != "your-openai-api-key":
        return "openai:gpt-4o"
    
    # Fallback to default (may fail if no keys configured)
    return settings.default_model


def get_task_extractor() -> Agent[Any, EmailTaskExtractor]:
    """
    Get the global task extraction agent instance.
    
    This function ensures the agent is created with the best available model
    when first accessed, rather than at module import time.
    
    Returns:
        Configured task extraction agent
    """
    global task_extractor
    if task_extractor is None:
        task_extractor = create_task_extraction_agent()
    return task_extractor


# Global task extraction agent instance - will be initialized when first used
task_extractor = None  # Will be initialized when first used
