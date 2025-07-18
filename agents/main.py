"""
Main orchestrator for AI Agents Swarm.

This module coordinates all agents and provides the main entry point
for the application. It handles:
- Agent initialization and coordination
- Background task scheduling
- Error handling and recovery
- System monitoring and logging
"""

import asyncio
import schedule
import time
from typing import List, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from loguru import logger

# Internal imports
from agents.core import Task, get_best_available_model, validate_model_availability
from agents.email_polling import EmailAgent
from agents.notion_integration import NotionAgent
from config.settings import settings


class AgentOrchestrator:
    """
    Main orchestrator that coordinates all agents.
    
    This class manages the lifecycle of all agents and coordinates
    their activities to create a seamless automation system.
    """
    
    def __init__(self, model: Optional[str] = None):
        """Initialize the orchestrator with all agents."""
        self.logger = logger.bind(component="orchestrator")
        self.logger.info("Initializing Agent Orchestrator")
        
        # Select the best available model if none specified
        self.model = model or get_best_available_model()
        
        # Validate model availability
        if not validate_model_availability(self.model):
            self.logger.warning(f"Model {self.model} may not be properly configured")
            
        self.logger.info(f"Using AI model: {self.model}")
        
        # Initialize agents with the selected model
        try:
            self.email_agent = EmailAgent(model=self.model)
            self.notion_agent = NotionAgent(model=self.model)
            
            # Validate Notion database setup
            if not self.notion_agent.validate_database_setup():
                raise ValueError("Notion database is not properly configured")
                
            self.logger.info("All agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
            raise
        
        # Task processing queue
        self.task_queue: List[Task] = []
        self.processing_lock = asyncio.Lock()
        
        # Background task executor
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # System stats
        self.stats = {
            "tasks_processed": 0,
            "emails_processed": 0,
            "errors": 0,
            "last_run": None,
            "uptime_start": datetime.now()
        }
    
    async def process_email_to_notion_pipeline(self, email_limit: int = 50, since_days: int = 7) -> None:
        """
        Main pipeline: Email → AI Analysis → Notion Task Creation.
        
        This is the core automation workflow that:
        1. Fetches new emails
        2. Extracts tasks using AI
        3. Creates tasks in Notion
        4. Updates tracking data
        
        Args:
            email_limit: Maximum number of emails to process
            since_days: Number of days back to check for emails
        """
        self.logger.info("Starting email-to-notion pipeline")
        
        try:
            # Step 1: Get new emails and extract tasks
            new_tasks = await self.email_agent.process_new_emails(since_days=since_days, limit=email_limit)
            
            if not new_tasks:
                self.logger.info("No new tasks to process")
                return
            
            # Step 2: Create tasks in Notion
            async with self.processing_lock:
                page_ids = await self.notion_agent.batch_create_tasks(new_tasks)
                
                # Update stats
                successful_tasks = len([pid for pid in page_ids if pid is not None])
                self.stats["tasks_processed"] += successful_tasks
                self.stats["emails_processed"] += len(new_tasks)
                self.stats["last_run"] = datetime.now()
                
                self.logger.info(f"Pipeline complete: {successful_tasks}/{len(new_tasks)} tasks created")
                
        except Exception as e:
            self.stats["errors"] += 1
            self.logger.error(f"Pipeline error: {e}")
            raise
    
    async def run_single_cycle(self, email_limit: int = 50, since_days: int = 7) -> None:
        """
        Run a single processing cycle.
        
        Args:
            email_limit: Maximum number of emails to process
            since_days: Number of days back to check for emails
        """
        try:
            await self.process_email_to_notion_pipeline(email_limit=email_limit, since_days=since_days)
        except Exception as e:
            self.logger.error(f"Cycle error: {e}")
    
    def schedule_background_tasks(self) -> None:
        """Set up background task scheduling."""
        if not settings.enable_background_tasks:
            self.logger.info("Background tasks disabled")
            return
        
        # Schedule email processing every N minutes
        interval_minutes = settings.email_check_interval // 60
        schedule.every(interval_minutes).minutes.do(
            lambda: asyncio.run(self.run_single_cycle())
        )
        
        # Schedule daily cleanup at 2 AM
        schedule.every().day.at("02:00").do(self.cleanup_old_data)
        
        self.logger.info(f"Scheduled background tasks (interval: {interval_minutes} minutes)")
    
    def cleanup_old_data(self) -> None:
        """Clean up old processed email data."""
        try:
            # This would clean up old processed email IDs
            # Keep only last 30 days of data
            self.logger.info("Cleaning up old data")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
    
    def get_system_stats(self) -> dict:
        """Get current system statistics."""
        uptime = datetime.now() - self.stats["uptime_start"]
        
        return {
            **self.stats,
            "uptime_seconds": uptime.total_seconds(),
            "uptime_hours": uptime.total_seconds() / 3600,
            "queue_size": len(self.task_queue),
            "email_agent_status": "active",
            "notion_agent_status": "active",
            "processed_emails_count": self.email_agent.get_processed_email_count() if self.email_agent else 0
        }
    
    def clear_processed_emails(self) -> None:
        """Clear processed emails for testing."""
        if self.email_agent:
            self.email_agent.clear_processed_emails()
            self.logger.info("Cleared processed emails")
    
    def force_email_processing(self, email_limit: int = 50, since_days: int = 7) -> None:
        """
        Force email processing for debugging.
        
        Args:
            email_limit: Maximum number of emails to process
            since_days: Number of days back to check for emails
        """
        self.logger.info("Forcing email processing")
        asyncio.run(self.process_email_to_notion_pipeline(email_limit=email_limit, since_days=since_days))
    
    def run_background_mode(self) -> None:
        """Run the orchestrator in background mode with scheduling."""
        self.logger.info("Starting background mode")
        
        # Set up scheduling
        self.schedule_background_tasks()
        
        # Main loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            self.logger.info("Shutting down gracefully...")
            self.executor.shutdown(wait=True)
        except Exception as e:
            self.logger.error(f"Background mode error: {e}")
            raise
    
    async def run_interactive_mode(self) -> None:
        """Run the orchestrator in interactive mode (single execution)."""
        self.logger.info("Running in interactive mode")
        
        try:
            await self.run_single_cycle()
            stats = self.get_system_stats()
            
            self.logger.info("Interactive mode complete")
            self.logger.info(f"Stats: {stats}")
            
        except Exception as e:
            self.logger.error(f"Interactive mode error: {e}")
            raise


def main():
    """Main entry point for the application."""
    # Configure logging
    logger.add(
        "logs/agents.log",
        rotation="1 day",
        retention="30 days",
        level=settings.log_level,
        format="{time} | {level} | {extra[component]} | {message}"
    )
    
    logger.info("Starting AI Agents Swarm")
    
    try:
        orchestrator = AgentOrchestrator()
        
        # Run in background mode by default
        if settings.enable_background_tasks:
            orchestrator.run_background_mode()
        else:
            # Run once in interactive mode
            asyncio.run(orchestrator.run_interactive_mode())
            
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise


if __name__ == "__main__":
    main()
