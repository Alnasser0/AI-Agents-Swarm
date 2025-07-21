# 🚀 AI Agents Swarm API

A robust FastAPI-based REST API that provides programmatic access to the AI Agents Swarm automation system. Built for scalability, real-time communication, and seamless integration.

## 🏗️ Architecture

The API serves as the central communication hub between the dashboard, agents, and external integrations:

```
api/
├── server.py              # Main FastAPI application
├── __init__.py           # Package initialization
└── __pycache__/          # Python cache files
```

## 🎯 Core Features

### **Real-time Communication**
- **WebSocket Support**: Live updates for dashboard and external clients
- **Connection Management**: Efficient WebSocket connection handling
- **Event Broadcasting**: Real-time notifications for system events

### **RESTful Endpoints**
- **Task Management**: Full CRUD operations for tasks and workflows
- **Agent Control**: Start, stop, and monitor agent operations
- **System Monitoring**: Health checks and performance metrics
- **Model Management**: AI model selection and configuration

### **Integration Ready**
- **CORS Support**: Cross-origin requests for web integrations
- **Webhook Support**: External system notifications and triggers

## 📡 API Endpoints

### **System Health & Monitoring**

#### `GET /health`
Basic health check endpoint
```json
{
  "status": "healthy",
  "timestamp": "2025-07-21T16:00:00.000Z"
}
```

#### `GET /health/detailed`
Comprehensive system health information
```json
{
  "status": "healthy",
  "timestamp": "2025-07-21T16:00:00.000Z",
  "agents": {
    "email": "active",
    "notion": "active"
  },
  "connections": {
    "notion_db": true,
    "email_server": true
  },
  "performance": {
    "memory_usage": "245MB",
    "cpu_usage": "12%",
    "uptime": "2d 4h 23m"
  }
}
```

### **Task Management**

#### `GET /api/tasks/recent`
Get recent tasks with optional filtering
```bash
GET /api/tasks/recent?limit=10&status=pending
```

#### `GET /api/stats`
System-wide statistics and metrics
```json
{
  "email_count": 1247,
  "task_count": 89,
  "agents_active": 2,
  "last_email_check": "2025-07-21T15:59:30.000Z",
  "uptime": "2d 4h 23m 15s",
  "errors_today": 0
}
```

### **Agent Control**

#### `GET /api/agents/status`
Current status of all agents
```json
{
  "email_agent": {
    "status": "active",
    "last_check": "2025-07-21T15:59:30.000Z",
    "emails_processed": 1247,
    "errors": 0
  },
  "notion_agent": {
    "status": "active",
    "tasks_created": 89,
    "last_sync": "2025-07-21T15:58:45.000Z",
    "database_health": "connected"
  }
}
```

#### `POST /api/agents/email/process`
Manually trigger email processing
```json
{
  "action": "process_emails",
  "limit": 50,
  "force": false
}
```

#### `POST /api/agents/notion/sync`
Force Notion database synchronization
```json
{
  "action": "sync_notion",
  "validate_schema": true
}
```

### **System Logs**

#### `GET /api/logs`
Retrieve system logs with filtering
```bash
GET /api/logs?limit=15&level=INFO&since=2025-07-21T00:00:00Z
```

### **AI Model Management**

#### `GET /api/models/available`
List all available AI models
```json
{
  "models": [
    {
      "id": "google-gla:gemini-2.0-flash",
      "name": "Gemini 2.0 Flash",
      "provider": "google",
      "status": "available",
      "tested": true
    },
    {
      "id": "anthropic:claude-3-5-sonnet-latest",
      "name": "Claude 3.5 Sonnet",
      "provider": "anthropic",
      "status": "available",
      "tested": false
    }
  ]
}
```

#### `GET /api/models/current`
Get currently active AI model
```json
{
  "current_model": "google-gla:gemini-2.0-flash",
  "fallback_models": ["anthropic:claude-3-5-sonnet-latest"],
  "performance": {
    "avg_response_time": "1.2s",
    "success_rate": "99.8%",
    "daily_requests": 342
  }
}
```

#### `POST /api/models/switch`
Switch to a different AI model
```json
{
  "model_id": "anthropic:claude-3-5-sonnet-latest",
  "update_default": true
}
```

### **Data Management**

#### `POST /api/data/sync-emails`
Sync past emails from specified timeframe
```json
{
  "days": 7,
  "limit": 50,
  "skip_duplicates": true
}
```

#### `POST /api/data/clear`
Clear system data (use with caution)
```json
{
  "clear_tasks": true,
  "clear_logs": false,
  "confirm": true
}
```

### **WebSocket Endpoints**

#### `WS /ws`
Real-time WebSocket connection for live updates
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

// Handle incoming messages
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  switch(message.type) {
    case 'stats_update':
      updateDashboardStats(message.data);
      break;
    case 'log_update':
      addLogEntry(message.data);
      break;
    case 'task_update':
      updateTasksList(message.data);
      break;
  }
};
```

## 🔧 Configuration

### **Server Settings**
```python
# FastAPI server configuration
CORS_ORIGINS = [
    "http://localhost:3000",  # React dashboard
]

API_HOST = "0.0.0.0"
API_PORT = 8000
DEBUG_MODE = False
```

### **WebSocket Management**
```python
# WebSocket connection limits
MAX_CONNECTIONS = 100
HEARTBEAT_INTERVAL = 30
CONNECTION_TIMEOUT = 300
```

## 🚀 Usage Examples

### **Python Client**
```python
import requests
import websocket

# REST API calls
response = requests.get('http://localhost:8000/api/stats')
stats = response.json()

# WebSocket connection
def on_message(ws, message):
    data = json.loads(message)
    print(f"Received: {data}")

ws = websocket.WebSocketApp(
    "ws://localhost:8000/ws",
    on_message=on_message
)
ws.run_forever()
```

### **JavaScript/React Integration**
```javascript
// API calls with fetch
const fetchStats = async () => {
  const response = await fetch('/api/stats');
  return response.json();
};

// WebSocket integration
const useWebSocket = (url) => {
  const [socket, setSocket] = useState(null);
  const [lastMessage, setLastMessage] = useState(null);
  
  useEffect(() => {
    const ws = new WebSocket(url);
    ws.onmessage = (event) => {
      setLastMessage(JSON.parse(event.data));
    };
    setSocket(ws);
    
    return () => ws.close();
  }, [url]);
  
  return { socket, lastMessage };
};
```

### **cURL Examples**
```bash
# Health check
curl http://localhost:8000/health

# Get system stats
curl http://localhost:8000/api/stats

# Trigger email processing
curl -X POST http://localhost:8000/api/agents/email/process \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}'

# Get recent tasks
curl "http://localhost:8000/api/tasks/recent?limit=5"
```

## 🔒 Security Features

### **CORS Configuration**
- Configured for dashboard origins
- Supports credentials for authenticated requests
- Flexible origin management for development and production

### **Input Validation**
- Pydantic models for request/response validation
- Automatic data sanitization
- Type checking and conversion

### **Error Handling**
- Comprehensive error responses
- Detailed logging without sensitive data exposure
- Graceful degradation for service failures

## 📊 Performance & Monitoring

### **Metrics Collection**
- Request/response time tracking
- Error rate monitoring
- WebSocket connection metrics
- Agent performance statistics

### **Health Monitoring**
- Automatic health checks for all components
- Dependency status monitoring
- Performance threshold alerting
- Graceful degradation handling

### **Logging**
- Structured JSON logging
- Request/response logging
- Error tracking with context
- Performance metrics logging

## 🛠️ Development

### **Running in Development**
```bash
# Start API server with auto-reload
uvicorn api.server:app --reload --host 0.0.0.0 --port 8000

# Or use the convenience script
python start.py  # Starts API + Dashboard + Agents
```

## 🚀 Deployment

### **Production Setup**
```bash
# Production server with gunicorn
gunicorn api.server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or with Docker
docker run -p 8000:8000 ai-agents-swarm-api
```

## 🤝 Contributing

### **API Development Guidelines**
1. **Follow FastAPI Patterns**: Use dependency injection and async/await
2. **Add Comprehensive Tests**: Unit and integration tests for new endpoints
3. **Document Endpoints**: Include detailed docstrings and examples
4. **Handle Errors Gracefully**: Proper HTTP status codes and error messages
5. **Maintain Backwards Compatibility**: Version API changes appropriately

### **Adding New Endpoints**
```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1")

class NewFeatureRequest(BaseModel):
    parameter: str
    options: dict = {}

@router.post("/new-feature")
async def create_new_feature(
    request: NewFeatureRequest,
    orchestrator = Depends(get_orchestrator)
):
    """Create a new feature with the given parameters."""
    try:
        result = await orchestrator.process_new_feature(request)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 📄 License

Part of the AI Agents Swarm project. See main LICENSE file for details.
