# 🤖 AI Agents Core

The core AI agents that power the intelligent email processing and task automation system.

## 🏗️ Architecture

The agents system is built with a modular architecture where each agent specializes in specific tasks but can work together through the central orchestrator.

```
agents/
├── main.py                 # AgentOrchestrator - Central coordination
├── core/                   # Base classes and shared utilities
├── email_polling/          # Email processing and real-time monitoring
├── notion_integration/     # Notion database management
└── slack_integration/      # Slack notifications (future)
```

## 🎯 Core Components

### **AgentOrchestrator** (`main.py`)
The central coordinator that manages all agents and workflows:

- **Agent Management**: Initializes and coordinates all specialized agents
- **Task Orchestration**: Routes tasks between agents based on type and priority
- **Real-time Monitoring**: Manages IMAP IDLE for instant email processing
- **Background Scheduling**: Handles periodic tasks and maintenance
- **Error Recovery**: Provides resilient error handling and recovery mechanisms
- **Health Monitoring**: Tracks system health and performance metrics

**Key Features:**
- Multi-AI model support with automatic fallback
- Real-time email monitoring with IMAP IDLE
- Intelligent duplicate detection
- Comprehensive logging and monitoring
- Background task scheduling

### **EmailAgent** (`email_polling/`)
Handles all email-related processing with intelligent filtering:

**Core Functionality:**
- **Real-time Processing**: IMAP IDLE for instant email notifications
- **Smart Filtering**: Only processes genuine human-to-human communications
- **Content Extraction**: Extracts actionable tasks from email content
- **Duplicate Prevention**: Prevents reprocessing of the same emails
- **Multiple Formats**: Supports HTML and plain text emails

**Intelligence Features:**
- Filters out automated emails (newsletters, notifications, etc.)
- Identifies actionable content vs. informational content
- Extracts context, urgency, and task details
- Maintains conversation threading awareness

### **NotionAgent** (`notion_integration/`)
Manages integration with Notion for task and knowledge management:

**Task Management:**
- **Automatic Task Creation**: Creates structured tasks from email content
- **Rich Metadata**: Adds context, priorities, deadlines, and categories
- **Database Validation**: Ensures proper schema and data consistency
- **Status Tracking**: Manages task lifecycle and completion states

## 🔧 Configuration

### **Agent Settings**
Each agent can be configured independently through environment variables:

```env
# Email Agent Configuration
EMAIL_CHECK_INTERVAL=300
ENABLE_REALTIME_EMAIL=true
REALTIME_FALLBACK_INTERVAL=180

# AI Model Configuration
DEFAULT_MODEL=google-gla:gemini-2.0-flash
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
GEMINI_API_KEY=your-key

# Processing Settings
LOG_LEVEL=INFO
ENABLE_BACKGROUND_TASKS=true
```

### **Notion Database Schema**
The system automatically validates and sets up the required Notion database schema:

- **Title**: Task title/summary
- **Description**: Detailed task description
- **Priority**: High/Medium/Low priority levels
- **Status**: Todo/In Progress/Done/Cancelled
- **Due Date**: Extracted deadlines and due dates
- **Category**: Automatic categorization by content
- **Source**: Email source and metadata
- **Created**: Timestamp of task creation

## 🚦 Usage

### **Standalone Operation**
```bash
# Run the agent system independently
python -m agents.main
```

### **API Integration**
```bash
# Run with FastAPI server
python start.py
```

### **Background Mode**
The agents can run in background mode for continuous processing:
- Real-time email monitoring
- Periodic health checks
- Automatic error recovery
- Performance optimization

## 🔍 Monitoring and Debugging

### **Logging System**
- **Structured Logging**: JSON-formatted logs for easy parsing
- **Multiple Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Performance Metrics**: Track processing times and success rates
- **Error Tracking**: Detailed error reporting with context

### **Health Monitoring**
- **Agent Status**: Monitor health of each individual agent
- **Connection Status**: Track API and service connectivity
- **Performance Metrics**: Monitor processing speed and efficiency
- **Resource Usage**: Track memory and CPU usage patterns

### **Debugging Tools**
- **Verbose Logging**: Enable detailed logging for troubleshooting
- **Test Mode**: Process sample emails without side effects
- **Manual Triggers**: Force processing of specific emails or tasks
- **Health Checks**: Validate all integrations and connections

## 🛠️ Development

### **Adding New Agents**
1. Create agent class inheriting from `BaseAgent`
2. Implement required methods: `process()`, `initialize()`, `health_check()`
3. Register agent in `AgentOrchestrator`
4. Add configuration and environment variables
5. Write tests and documentation

## 🤝 Contributing

When contributing to the agents system:

1. **Follow Architecture**: Maintain modular, single-responsibility design
2. **Add Tests**: Include unit and integration tests
3. **Document Changes**: Update documentation for new features
4. **Performance Testing**: Ensure changes don't impact performance
5. **Error Handling**: Implement comprehensive error handling

## 📄 License

Part of the AI Agents Swarm project. See main LICENSE file for details.
