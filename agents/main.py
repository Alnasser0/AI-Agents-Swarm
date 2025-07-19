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
from agents.email_polling.realtime import RealTimeEmailProcessor
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
            
            # Initialize real-time email processor
            self.realtime_processor = RealTimeEmailProcessor(
                email_callback=self._realtime_email_callback
            )
            
            # Auto-start real-time monitoring if enabled
            if getattr(settings, 'enable_realtime_email', True):
                # Start in a separate thread to avoid blocking initialization
                import threading
                threading.Thread(
                    target=self._start_realtime_delayed,
                    daemon=True
                ).start()
            
            # Validate Notion database setup
            if not self.notion_agent.validate_database_setup():
                raise ValueError("Notion database is not properly configured")
                
            self.logger.info("All agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {e}")
            raise
        
        # Task processing queue
        self.task_queue: List[Task] = []
        self.processing_lock = None  # Initialize lazily to avoid event loop issues
        
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
    
    def _get_processing_lock(self):
        """Get the processing lock, creating it if necessary."""
        if self.processing_lock is None:
            self.processing_lock = asyncio.Lock()
        return self.processing_lock
    
    async def _realtime_email_callback(self):
        """Callback for real-time email processing."""
        try:
            self.logger.info("Processing real-time email notification")
            # Process emails immediately with smaller batch for speed
            await self.process_email_to_notion_pipeline(email_limit=10, since_days=1)
        except Exception as e:
            self.logger.error(f"Real-time email processing error: {e}")
    
    def _start_realtime_delayed(self):
        """Start real-time monitoring with a delay to allow initialization to complete."""
        import time
        time.sleep(2)  # Wait for initialization to complete
        try:
            self.start_realtime_monitoring()
        except Exception as e:
            self.logger.error(f"Failed to auto-start real-time monitoring: {e}")
    
    async def process_email_to_notion_pipeline(self, email_limit: int = 50, since_days: int = 7) -> None:
        """
        Main pipeline: Email → AI Analysis → Notion Task Creation.
        
        This is the core automation workflow that:
        1. Fetches new emails
        2. Extracts tasks using AI
        3. Creates tasks in Notion
        4. Updates tracking data
        """
        self.logger.info("Starting email-to-notion pipeline")
        
        try:
            # Step 1: Get new emails and extract tasks
            new_tasks = await self.email_agent.process_new_emails(since_days=since_days, limit=email_limit)
            
            if not new_tasks:
                self.logger.info("No new tasks to process")
                return
            
            # Step 2: Create tasks in Notion
            processing_lock = self._get_processing_lock()
            async with processing_lock:
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
    
    async def run_single_cycle(self, email_limit: Optional[int] = None, since_days: Optional[int] = None) -> None:
        """
        Run a single processing cycle.
        
        Args:
            email_limit: Maximum number of emails to process (uses default if None)
            since_days: Days back to search for emails (uses default if None)
        """
        try:
            # Use provided parameters or fall back to defaults
            if email_limit is not None or since_days is not None:
                await self.process_email_to_notion_pipeline(
                    email_limit=email_limit or 50,
                    since_days=since_days or 7
                )
            else:
                # Use method defaults
                await self.process_email_to_notion_pipeline()
        except Exception as e:
            self.logger.error(f"Cycle error: {e}")
    
    def schedule_background_tasks(self) -> None:
        """Set up background task scheduling."""
        if not settings.enable_background_tasks:
            self.logger.info("Background tasks disabled")
            return
        
        # Schedule email processing every N minutes
        interval_minutes = getattr(self, 'check_interval_minutes', settings.email_check_interval // 60)
        schedule.every(interval_minutes).minutes.do(
            lambda: asyncio.run(self.run_single_cycle_with_config())
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
        
        # Get real-time email status
        realtime_status = self.get_realtime_status()
        
        return {
            **self.stats,
            "uptime_seconds": uptime.total_seconds(),
            "uptime_hours": uptime.total_seconds() / 3600,
            "queue_size": len(self.task_queue),
            "email_agent_status": "active",
            "notion_agent_status": "active",
            "realtime_email": realtime_status  # Add real-time status
        }
    
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
    
    def start_realtime_monitoring(self):
        """Start real-time email monitoring."""
        try:
            if self.realtime_processor:
                self.realtime_processor.start_idle_monitoring()
                self.logger.info("Real-time email monitoring started")
        except Exception as e:
            self.logger.error(f"Failed to start real-time monitoring: {e}")
    
    def stop_realtime_monitoring(self):
        """Stop real-time email monitoring."""
        try:
            if self.realtime_processor:
                self.realtime_processor.stop_idle_monitoring()
                self.logger.info("Real-time email monitoring stopped")
        except Exception as e:
            self.logger.error(f"Failed to stop real-time monitoring: {e}")
    
    def get_realtime_status(self) -> dict:
        """Get real-time monitoring status."""
        if self.realtime_processor:
            return self.realtime_processor.get_status()
        return {"idle_running": False, "idle_thread_alive": False, "last_idle_restart": None, "idle_supported": False}
    
    def configure_email_processing(self, email_limit: int = 50, since_days: int = 7, check_interval_minutes: int = 5):
        """
        Configure email processing parameters.
        
        Args:
            email_limit: Maximum number of emails to process per cycle
            since_days: Days back to search for emails
            check_interval_minutes: How often to check for new emails
        """
        self.email_limit = email_limit
        self.since_days = since_days
        self.check_interval_minutes = check_interval_minutes
        
        self.logger.info(f"Email processing configured: {email_limit} emails, {since_days} days back, {check_interval_minutes}min interval")
    
    async def run_single_cycle_with_config(self) -> None:
        """Run a single cycle using configured parameters."""
        email_limit = getattr(self, 'email_limit', 50)
        since_days = getattr(self, 'since_days', 7)
        
        await self.run_single_cycle(email_limit=email_limit, since_days=since_days)


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
