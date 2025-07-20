"""
FastAPI server for AI Agents Swarm.

This provides a REST API for the agent system, enabling external
integrations and programmatic control. Features include:
- Agent status endpoints
- Manual trigger endpoints
- Task creation and management
- System statistics
- Webhook support for future integrations
- WebSocket support for real-time updates
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import asyncio
import uvicorn
import json
from loguru import logger

# Internal imports
from agents.main import AgentOrchestrator
from agents.core import Task, TaskPriority, TaskStatus
from config.settings import settings


# JSON Encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def serialize_datetime_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively serialize datetime objects in a dictionary to ISO format."""
    if isinstance(data, dict):
        return {key: serialize_datetime_dict(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_datetime_dict(item) for item in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    else:
        return data


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


class WebSocketManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """Accept a WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        if not self.active_connections:
            return
        
        # Serialize datetime objects before JSON encoding
        serialized_message = serialize_datetime_dict(message)
        message_str = json.dumps(serialized_message)
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception:
                disconnected.add(connection)
        
        # Clean up disconnected connections
        self.active_connections -= disconnected
        
        if disconnected:
            logger.info(f"Cleaned up {len(disconnected)} disconnected WebSocket connections")
    
    async def send_stats_update(self, stats: dict):
        """Send stats update to all clients."""
        # Serialize stats dict to handle datetime objects
        serialized_stats = serialize_datetime_dict(stats)
        await self.broadcast({
            "type": "stats_update",
            "data": serialized_stats,
            "timestamp": datetime.now().isoformat()
        })
    
    async def send_log_update(self, log_entry: dict):
        """Send log update to all clients."""
        await self.broadcast({
            "type": "log_update", 
            "data": log_entry,
            "timestamp": datetime.now().isoformat()
        })
    
    async def send_task_update(self, task_data: dict):
        """Send task update to all clients."""
        await self.broadcast({
            "type": "task_update",
            "data": task_data,
            "timestamp": datetime.now().isoformat()
        })


# Global WebSocket manager
websocket_manager = WebSocketManager()


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
        # Connect WebSocket manager to orchestrator for real-time updates
        orchestrator.set_websocket_manager(websocket_manager)
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
            "stats": "/api/stats",
            "agents": "/api/agents/status", 
            "tasks": "/api/tasks/recent",
            "logs": "/api/logs",
            "realtime_status": "/api/realtime/status",
            "config": "/api/config",
            "websocket": "/ws",
            "triggers": {
                "email_processing": "/api/trigger/email-processing",
                "full_pipeline": "/api/trigger/full-pipeline",
                "realtime_start": "/api/realtime/start",
                "realtime_stop": "/api/realtime/stop"
            },
            "webhook": "/webhook/email"
        }
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket_manager.connect(websocket)
    try:
        # Send initial data
        if orchestrator:
            # Use get_system_stats() instead of raw stats to handle datetime serialization
            system_stats = orchestrator.get_system_stats()
            await websocket_manager.send_stats_update(system_stats)
            
            # Send recent logs
            for log_entry in orchestrator.log_buffer[-10:]:  # Last 10 logs
                await websocket_manager.send_log_update(log_entry)
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                # Handle any client messages if needed
                logger.debug(f"Received WebSocket message: {data}")
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        await websocket_manager.disconnect(websocket)


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
        tasks_processed=stats["tasks_created"],  # Map to new field name
        emails_processed=stats["emails_processed"],
        errors=stats["errors"],
        uptime_hours=stats["uptime_hours"],
        last_run=stats.get("last_run"),
        agent_status={
            "email": stats["email_agent_status"],
            "notion": stats["notion_agent_status"]
        }
    )


@app.get("/api/stats")
async def get_api_stats():
    """Get system statistics (API endpoint for dashboard)."""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        stats = orchestrator.get_system_stats()
        
        return {
            "emails_processed": stats.get("emails_processed", 0),
            "tasks_created": stats.get("tasks_created", 0),  # Changed from tasks_processed
            "processed_emails_count": stats.get("processed_emails_count", 0),
            "uptime_hours": stats.get("uptime_hours", 0.0),
            "errors": stats.get("errors", 0),
            "realtime_email": {
                "idle_supported": stats.get("idle_supported", True),
                "idle_running": stats.get("idle_running", False),
                "idle_thread_alive": stats.get("idle_thread_alive", False),
                "status": stats.get("realtime_status", "inactive")
            }
        }
    except Exception as e:
        # Return default stats if orchestrator fails
        return {
            "emails_processed": 0,
            "tasks_processed": 0,
            "processed_emails_count": 0,
            "uptime_hours": 0.0,
            "errors": 0,
            "realtime_email": {
                "idle_supported": True,
                "idle_running": False,
                "idle_thread_alive": False,
                "status": "inactive"
            }
        }


@app.get("/api/agents/status")
async def get_agents_status():
    """Get status of all agents (API endpoint for dashboard)."""
    if orchestrator is None:
        return []
    
    try:
        agents = []
        
        # Email agent status
        if hasattr(orchestrator, 'email_agent'):
            from config.settings import settings
            agents.append({
                "name": "Email Agent",
                "status": "online" if orchestrator.email_agent else "offline",
                "provider": getattr(settings, 'email_provider', 'IMAP'),
                "account": getattr(settings, 'email_address', 'user@example.com'),
                "interval": f"{getattr(settings, 'email_check_interval', 5)} minutes"
            })
        
        # Notion agent status
        if hasattr(orchestrator, 'notion_agent'):
            try:
                db_valid = orchestrator.notion_agent.validate_database_setup()
                schema_status = "✅ Valid" if db_valid else "❌ Invalid"
            except:
                schema_status = "❌ Invalid"
                
            agents.append({
                "name": "Notion Agent",
                "status": "online" if orchestrator.notion_agent else "offline",
                "database": "tasks...",
                "schema": schema_status
            })
        
        return agents
    except Exception as e:
        # Return default agents if something fails
        return [
            {
                "name": "Email Agent",
                "status": "offline",
                "provider": "IMAP",
                "account": "user@example.com",
                "interval": "5 minutes"
            },
            {
                "name": "Notion Agent",
                "status": "offline",
                "database": "tasks...",
                "schema": "❌ Invalid"
            }
        ]


@app.get("/api/tasks/recent")
async def get_api_recent_tasks(limit: int = 10):
    """Get recent tasks (API endpoint for dashboard)."""
    try:
        if orchestrator is None:
            return []
            
        # Get real tasks from Notion database
        if hasattr(orchestrator, 'notion_agent') and orchestrator.notion_agent:
            # Query recent tasks from Notion
            recent_tasks = orchestrator.notion_agent.get_recent_tasks(limit=limit)
            return recent_tasks
        else:
            # Return empty list if no real tasks yet
            return []
        
    except Exception as e:
        print(f"Error getting tasks: {e}")
        return []


@app.get("/api/logs")
async def get_api_logs(limit: int = 15):
    """Get system logs (API endpoint for dashboard)."""
    if orchestrator is None:
        # Return empty logs if orchestrator is not initialized
        return []
    
    try:
        # Get real-time logs from orchestrator
        logs = orchestrator.get_recent_logs(limit)
        
        # If no logs yet, add a default entry
        if not logs:
            from datetime import datetime
            logs = [{
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "component": "System",
                "message": "System ready - waiting for events"
            }]
        
        return logs
        
    except Exception as e:
        # Fallback to basic log if there's an error
        from datetime import datetime
        return [{
            "timestamp": datetime.now().isoformat(),
            "level": "ERROR",
            "component": "API",
            "message": f"Error retrieving logs: {e}"
        }]


@app.get("/api/realtime/status")
async def get_realtime_status():
    """Get real-time status (API endpoint for dashboard)."""
    if orchestrator is None:
        return {
            "idle_supported": False,
            "idle_running": False,
            "idle_thread_alive": False,
            "status": "inactive",
            "last_check": None
        }
    
    try:
        stats = orchestrator.get_system_stats()
        return {
            "idle_supported": stats.get("idle_supported", True),
            "idle_running": stats.get("idle_running", False),
            "idle_thread_alive": stats.get("idle_thread_alive", False),
            "status": stats.get("realtime_status", "inactive"),
            "last_check": stats.get("last_realtime_check")
        }
    except Exception as e:
        return {
            "idle_supported": False,
            "idle_running": False,
            "idle_thread_alive": False,
            "status": "error",
            "last_check": None
        }


@app.get("/api/config")
async def get_system_configuration():
    """Get system configuration (API endpoint for dashboard)."""
    from config.settings import settings
    
    return {
        "email_provider": settings.email_provider,
        "email_address": settings.email_address,
        "email_check_interval": settings.email_check_interval,
        "enable_realtime_email": settings.enable_realtime_email,
        "default_model": settings.default_model,
        "timezone": settings.timezone,
        "api_host": settings.api_host,
        "api_port": settings.api_port
    }


@app.post("/api/trigger/email-processing")
async def trigger_email_processing_api(background_tasks: BackgroundTasks):
    """Trigger email processing manually (API endpoint for dashboard)."""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        # Run email processing in background
        background_tasks.add_task(orchestrator.run_single_cycle)
        
        return {
            "success": True,
            "message": "Email processing triggered successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to trigger email processing: {e}"
        }


@app.post("/api/trigger/full-pipeline")
async def trigger_full_pipeline_api(background_tasks: BackgroundTasks):
    """Trigger full pipeline manually (API endpoint for dashboard)."""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        # Run full pipeline in background
        background_tasks.add_task(orchestrator.process_email_to_notion_pipeline, 10, 1)
        
        return {
            "success": True,
            "message": "Full pipeline triggered successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to trigger full pipeline: {e}"
        }


@app.post("/api/realtime/start")
async def start_realtime_monitoring_api():
    """Start real-time monitoring (API endpoint for dashboard)."""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        orchestrator.start_realtime_monitoring()
        return {
            "success": True,
            "message": "Real-time monitoring started"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to start real-time monitoring: {e}"
        }


@app.post("/api/realtime/stop")
async def stop_realtime_monitoring_api():
    """Stop real-time monitoring (API endpoint for dashboard)."""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        orchestrator.stop_realtime_monitoring()
        return {
            "success": True,
            "message": "Real-time monitoring stopped"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to stop real-time monitoring: {e}"
        }


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


class SyncRequest(BaseModel):
    """API model for sync past emails request."""
    days: int = 7
    limit: int = 50


@app.post("/api/management/sync-past-emails", response_model=TriggerResponse)
async def sync_past_emails(
    request: SyncRequest,
    background_tasks: BackgroundTasks
):
    """Sync past emails by processing historical emails."""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    # Validate parameters
    if request.days < 1 or request.days > 365:
        return TriggerResponse(
            success=False,
            message="Days must be between 1 and 365"
        )
    
    if request.limit < 1 or request.limit > 1000:
        return TriggerResponse(
            success=False,
            message="Limit must be between 1 and 1000"
        )
    
    try:
        # Run historical email processing in background
        background_tasks.add_task(
            orchestrator.process_email_to_notion_pipeline,
            email_limit=request.limit,
            since_days=request.days
        )
        
        return TriggerResponse(
            success=True,
            message=f"Historical email sync triggered for last {request.days} days (limit: {request.limit})"
        )
    except Exception as e:
        return TriggerResponse(
            success=False,
            message=f"Failed to sync past emails: {e}"
        )


@app.post("/api/management/clear-data", response_model=TriggerResponse)
async def clear_processed_data():
    """Clear all processed email data and cache."""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        # Clear processed emails cache
        orchestrator.email_agent.clear_processed_emails()
        
        # Reset stats
        orchestrator.stats["emails_processed"] = 0
        orchestrator.stats["tasks_processed"] = 0
        orchestrator.stats["errors"] = 0
        
        return TriggerResponse(
            success=True,
            message="All processed data cleared successfully"
        )
    except Exception as e:
        return TriggerResponse(
            success=False,
            message=f"Failed to clear data: {e}"
        )


@app.get("/api/models/available")
async def get_available_models():
    """Get list of available AI models with status indicators."""
    try:
        from agents.core import get_available_models, validate_model_availability
        
        models_by_provider = get_available_models()
        model_status = {}
        
        for provider, models in models_by_provider.items():
            model_status[provider] = []
            for model in models:
                is_available = validate_model_availability(model)
                model_info = {
                    "id": model,
                    "name": model.split(":")[-1],  # Extract model name from provider:model format
                    "provider": provider,
                    "available": is_available,
                    "status": "available" if is_available else "unavailable"
                }
                model_status[provider].append(model_info)
        
        return {
            "models": model_status,
            "current_model": orchestrator.model if orchestrator else None
        }
    except Exception as e:
        logger.error(f"Failed to get available models: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get available models: {str(e)}")


@app.get("/api/models/current")
async def get_current_model():
    """Get the currently selected model."""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        from agents.core import validate_model_availability
        
        current_model = orchestrator.model
        is_available = validate_model_availability(current_model)
        
        return {
            "model": current_model,
            "available": is_available,
            "status": "available" if is_available else "unavailable"
        }
    except Exception as e:
        logger.error(f"Failed to get current model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get current model: {str(e)}")


@app.post("/api/models/switch", response_model=TriggerResponse)
async def switch_model(model_data: dict):
    """Switch to a different AI model."""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        from agents.core import validate_model_availability
        
        new_model = model_data.get("model")
        if not new_model:
            return TriggerResponse(
                success=False,
                message="Model is required"
            )
        
        # Validate the model is available
        if not validate_model_availability(new_model):
            return TriggerResponse(
                success=False,
                message=f"Model {new_model} is not available or not properly configured"
            )
        
        # Switch the model in the orchestrator
        old_model = orchestrator.model
        orchestrator.switch_model(new_model)
        
        logger.info(f"Model switched from {old_model} to {new_model}")
        
        return TriggerResponse(
            success=True,
            message=f"Model switched from {old_model} to {new_model}"
        )
    except Exception as e:
        logger.error(f"Failed to switch model: {e}")
        return TriggerResponse(
            success=False,
            message=f"Failed to switch model: {str(e)}"
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
        if orchestrator:
            await orchestrator.process_email_to_notion_pipeline(email_limit=10, since_days=1)
        else:
            print("Orchestrator not available for webhook processing")
            
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
