"""
Configuration management for AI Agents Swarm.

This module handles all configuration through environment variables
and provides a centralized settings object for the entire application.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings are loaded from .env file or environment variables.
    This provides a single source of truth for configuration.
    """
    
    # Email Settings
    email_provider: str = Field(default="gmail", description="Email provider (gmail, outlook, etc.)")
    email_address: str = Field(description="Email address to monitor")
    email_password: str = Field(description="Email password or app password")
    email_imap_server: str = Field(default="imap.gmail.com", description="IMAP server")
    email_imap_port: int = Field(default=993, description="IMAP port")
    email_check_interval: int = Field(default=300, description="Email check interval in seconds")
    
    # Notion Settings
    notion_api_key: str = Field(description="Notion integration API key")
    notion_database_id: str = Field(description="Notion database ID for tasks")
    
    # Slack Settings (future)
    slack_bot_token: Optional[str] = Field(default=None, description="Slack bot token")
    slack_signing_secret: Optional[str] = Field(default=None, description="Slack signing secret")
    
    # AI Model Settings
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    default_model: str = Field(default="anthropic:claude-3-5-sonnet-latest", description="Default AI model")
    
    # Application Settings
    log_level: str = Field(default="INFO", description="Logging level")
    enable_background_tasks: bool = Field(default=True, description="Enable background task processing")
    timezone: str = Field(default="UTC", description="Application timezone")
    
    # Dashboard Settings
    dashboard_host: str = Field(default="localhost", description="Dashboard host")
    dashboard_port: int = Field(default=8501, description="Dashboard port")
    api_host: str = Field(default="localhost", description="API host")
    api_port: int = Field(default=8000, description="API port")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
