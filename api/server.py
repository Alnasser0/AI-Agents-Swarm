"""
FastAPI server for AI Agents Swarm.

This provides a REST API for the agent system, enabling external
integrations and programmatic control. Features include:
- Agent status endpoints
- Manual trigger endpoints
- Task creation and management
- System statistics
- Webhook support for future integrations
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import uvicorn

# Internal imports
from agents.main import AgentOrchestrator
from agents.core import Task, TaskPriority, TaskStatus
from config.settings import settings


# API Models
class TaskCreate(BaseModel):
    """API model for creating tasks."""
    title: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    tags: List[str] = []
    source: str = "api"


class TaskResponse(BaseModel):
    """API model for task responses."""
    id: str
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus
    source: str
    created_at: datetime
    due_date: Optional[datetime] = None
    tags: List[str] = []


class SystemStats(BaseModel):
    """API model for system statistics."""
    tasks_processed: int
    emails_processed: int
    errors: int
    uptime_hours: float
    last_run: Optional[datetime]
    agent_status: Dict[str, str]


class TriggerResponse(BaseModel):
    """API model for trigger responses."""
    success: bool
    message: str
    tasks_created: Optional[int] = None


# Initialize FastAPI app
app = FastAPI(
    title="AI Agents Swarm API",
    description="REST API for the AI Agents Swarm automation system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator = None


@app.on_event("startup")
async def startup_event():
    """Initialize the agent orchestrator on startup."""
    global orchestrator
    try:
        orchestrator = AgentOrchestrator()
    except Exception as e:
        raise RuntimeError(f"Failed to initialize orchestrator: {e}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint with system info."""
    return {
        "name": "AI Agents Swarm API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "tasks": "/tasks",
            "agents": "/agents",
            "webhook": "/webhook/email"
        }
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check endpoint."""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents": {
            "email": "active",
            "notion": "active"
        }
    }


@app.get("/stats", response_model=SystemStats)
async def get_system_stats():
    """Get system statistics."""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    stats = orchestrator.get_system_stats()
    
    return SystemStats(
        tasks_processed=stats["tasks_processed"],
        emails_processed=stats["emails_processed"],
        errors=stats["errors"],
        uptime_hours=stats["uptime_hours"],
        last_run=stats.get("last_run"),
        agent_status={
            "email": stats["email_agent_status"],
            "notion": stats["notion_agent_status"]
        }
    )


@app.post("/trigger/email", response_model=TriggerResponse)
async def trigger_email_processing(background_tasks: BackgroundTasks):
    """Trigger email processing manually."""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        # Run email processing in background
        background_tasks.add_task(orchestrator.run_single_cycle)
        
        return TriggerResponse(
            success=True,
            message="Email processing triggered successfully"
        )
    except Exception as e:
        return TriggerResponse(
            success=False,
            message=f"Failed to trigger email processing: {e}"
        )


@app.post("/trigger/pipeline", response_model=TriggerResponse)
async def trigger_full_pipeline(background_tasks: BackgroundTasks):
    """Trigger the full email-to-notion pipeline."""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        # Run full pipeline in background
        background_tasks.add_task(orchestrator.process_email_to_notion_pipeline)
        
        return TriggerResponse(
            success=True,
            message="Full pipeline triggered successfully"
        )
    except Exception as e:
        return TriggerResponse(
            success=False,
            message=f"Failed to trigger pipeline: {e}"
        )


@app.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate):
    """Create a new task manually."""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        # Create task object
        new_task = Task(
            title=task.title,
            description=task.description,
            priority=task.priority,
            source=task.source,
            due_date=task.due_date,
            tags=task.tags,
            metadata={"created_via": "api"}
        )
        
        # Create in Notion
        page_id = orchestrator.notion_agent.create_task_in_notion(new_task)
        
        if page_id:
            return TaskResponse(
                id=page_id,
                title=new_task.title,
                description=new_task.description,
                priority=new_task.priority,
                status=new_task.status,
                source=new_task.source,
                created_at=new_task.created_at,
                due_date=new_task.due_date,
                tags=new_task.tags
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create task in Notion")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create task: {e}")


@app.get("/tasks/recent")
async def get_recent_tasks(limit: int = 10):
    """Get recent tasks (placeholder for now)."""
    # This would integrate with Notion to fetch recent tasks
    return {
        "message": "Recent tasks endpoint - to be implemented",
        "limit": limit
    }


@app.get("/agents/email/status")
async def get_email_agent_status():
    """Get email agent status."""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    return {
        "status": "active",
        "provider": settings.email_provider,
        "account": settings.email_address,
        "imap_server": settings.email_imap_server,
        "check_interval": settings.email_check_interval,
        "last_check": None  # Would track last check time
    }


@app.get("/agents/notion/status")
async def get_notion_agent_status():
    """Get Notion agent status."""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    # Check database connectivity
    db_valid = orchestrator.notion_agent.validate_database_setup()
    
    return {
        "status": "active" if db_valid else "error",
        "database_id": settings.notion_database_id,
        "database_valid": db_valid
    }


@app.post("/webhook/email")
async def email_webhook(data: dict, background_tasks: BackgroundTasks):
    """
    Webhook endpoint for email notifications.
    
    This endpoint receives notifications from email services and triggers
    immediate email processing for faster response times.
    """
    try:
        if orchestrator is None:
            raise HTTPException(status_code=503, detail="System not initialized")
        
        # Log webhook receipt
        print(f"Email webhook received: {data}")
        
        # Add background task to process emails immediately
        background_tasks.add_task(
            _process_webhook_email,
            data
        )
        
        return {
            "message": "Email webhook received and processing started",
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook processing error: {str(e)}")


async def _process_webhook_email(webhook_data: dict):
    """Process email webhook in background."""
    try:
        if orchestrator and hasattr(orchestrator, 'realtime_processor'):
            orchestrator.realtime_processor.process_webhook_notification(webhook_data)
        else:
            # Fallback to immediate email processing
            await orchestrator.process_email_to_notion_pipeline(email_limit=10, since_days=1)
            
    except Exception as e:
        print(f"Background webhook processing error: {e}")


@app.get("/webhook/email/test")
async def test_email_webhook():
    """Test endpoint to trigger email webhook processing."""
    test_data = {
        "provider": "gmail",
        "event": "new_email",
        "timestamp": datetime.now().isoformat(),
        "test": True
    }
    
    background_tasks = BackgroundTasks()
    return await email_webhook(test_data, background_tasks)


def run_server():
    """Run the FastAPI server."""
    uvicorn.run(
        "api.server:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    run_server()
