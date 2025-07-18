# 🤖 AI Agents Swarm

A powerful, modular automation system that transforms your email inbox into an intelligent task management workflow. Built with modern AI agents that work together to extract, process, and organize tasks automatically.

## 🌟 Key Features

### 🚀 **Real-time & Resilient Processing**
- **IMAP IDLE**: Instant email processing (no waiting!)
- **Polling Fallback**: 5-minute intervals for reliability
- **Webhook Support**: External integration endpoints
- **Duplicate Detection**: Automatic prevention of duplicate tasks

### 🧠 **AI-Powered Intelligence**
- **Multi-Model Support**: OpenAI GPT, Anthropic Claude, Google Gemini
- **Dynamic Fallback**: Automatically switches between AI providers
- **Smart Extraction**: Only processes genuine human-to-human tasks
- **Context Awareness**: Understands email context and urgency

### 🎯 **Seamless Integration**
- **Notion**: Automatic task creation with rich metadata
- **Email**: Gmail, Outlook, and other IMAP providers
- **Slack**: (Coming soon) Team notifications and updates
- **REST API**: Full programmatic control

### 🎨 **Beautiful Dashboard**
- **Real-time Status**: Live monitoring of all components
- **Manual Controls**: Force processing, clear data, debug tools
- **System Stats**: Performance metrics and health indicators
- **User-Friendly**: Clean, intuitive interface

## 🚀 Quick Start

### **One Command Setup**

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/AI-Agents-Swarm.git
cd AI-Agents-Swarm

# 2. Set up environment
conda create -n ai python=3.11
conda activate ai
pip install -r requirements.txt

# 3. Configure your settings
cp .env.example .env
# Edit .env with your API keys and email settings

# 4. Start everything with ONE command
python start.py
```

**Or on Windows, just double-click `start.bat`!**

That's it! The system will automatically:
- ✅ Start the API server (http://localhost:8000)
- ✅ Launch the dashboard (http://localhost:8501)
- ✅ Initialize real-time email monitoring
- ✅ Open your browser to the dashboard

## 📖 How It Works

### **The Magic Workflow**

```
📧 Email Arrives
    ↓
⚡ IMAP IDLE Detects (Instant!)
    ↓
🤖 AI Analyzes Content
    ↓
🎯 Extracts Tasks (Smart Filtering)
    ↓
🔍 Checks for Duplicates
    ↓
📝 Creates Notion Tasks
    ↓
✅ Updates Dashboard
```

### **Dual Processing System**

1. **Real-time Processing**: IMAP IDLE for instant notifications
2. **Fallback Polling**: Every 5 minutes for reliability
3. **Webhook Integration**: External systems can trigger processing

### **AI-Powered Task Extraction**

The system uses advanced AI to:
- Identify genuine tasks vs. automated emails
- Extract task details (title, description, priority, due date)
- Classify and tag tasks appropriately
- Prevent duplicate task creation

## 🔧 Configuration

### **Environment Variables**

```env
# Email Settings
EMAIL_ADDRESS=your.email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_IMAP_SERVER=imap.gmail.com
EMAIL_IMAP_PORT=993
EMAIL_CHECK_INTERVAL=300  # 5 minutes fallback polling
ENABLE_REALTIME_EMAIL=true  # Enable IMAP IDLE

# AI Model Settings (at least one required)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GEMINI_API_KEY=your-gemini-key
DEFAULT_MODEL=anthropic:claude-3-5-sonnet-latest

# Notion Settings
NOTION_API_KEY=your-notion-integration-key
NOTION_DATABASE_ID=your-database-id

# Application Settings
LOG_LEVEL=INFO
DASHBOARD_PORT=8501
API_PORT=8000
```

### **Supported AI Models**

- **OpenAI**: `openai:gpt-4`, `openai:gpt-3.5-turbo`
- **Anthropic**: `anthropic:claude-3-5-sonnet-latest`, `anthropic:claude-3-haiku-latest`
- **Google**: `google-gla:gemini-2.5-flash`, `google-gla:gemini-1.5-pro`

## 🎛️ Dashboard Features

### **Real-time Status**
- **Agent Status**: Live monitoring of all components
- **Email Processing**: Real-time vs. polling status
- **Task Statistics**: Processed emails, created tasks, errors

### **Manual Controls**
- **Force Processing**: Trigger immediate email processing
- **Custom Batch**: Process specific number of emails
- **Clear Data**: Reset processed email tracking
- **Real-time Toggle**: Start/stop IMAP IDLE monitoring

### **System Information**
- **Recent Tasks**: Latest processed tasks
- **System Logs**: Real-time log monitoring
- **Health Metrics**: Performance and error tracking

## 🔌 API Endpoints

### **Core Endpoints**
- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

### **Task Management**
- `GET /tasks` - List all tasks
- `POST /tasks` - Create new task
- `GET /tasks/{id}` - Get specific task

### **Agent Control**
- `GET /agents/status` - Agent status
- `POST /agents/email/process` - Trigger email processing
- `GET /agents/email/stats` - Email processing statistics

### **Webhooks**
- `POST /webhook/email` - Email notification webhook
- `GET /webhook/email/test` - Test webhook processing

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Dashboard     │    │   API Server    │    │  Email Agent    │
│   (Streamlit)   │◄──►│   (FastAPI)     │◄──►│  (IMAP IDLE)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Orchestrator   │◄──►│   AI Models     │◄──►│  Notion Agent   │
│  (Coordinator)  │    │ (Multi-provider)│    │  (Task Creator) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Key Components**

1. **AgentOrchestrator**: Coordinates all agents and workflows
2. **EmailAgent**: Handles email processing and real-time monitoring
3. **NotionAgent**: Manages Notion integration and task creation
4. **RealTimeEmailProcessor**: IMAP IDLE implementation
5. **Dashboard**: Streamlit-based user interface
6. **API Server**: FastAPI-based REST API

## 🔍 Troubleshooting

### **Common Issues**

**Real-time shows "Starting..." forever**
- Check your email credentials
- Ensure IMAP is enabled in your email provider
- Verify firewall/network connectivity

**API server not responding**
- Make sure port 8000 is available
- Check if another process is using the port
- Verify your .env configuration

**Tasks not appearing in Notion**
- Check Notion API key and database ID
- Ensure the database schema is correct
- Verify the integration has proper permissions

**AI model errors**
- Ensure at least one AI API key is configured
- Check API key validity and quotas
- Review model availability and naming

### **Debug Mode**

Enable debug mode for detailed logging:

```env
LOG_LEVEL=DEBUG
```

Use the dashboard's debug controls:
- **Clear Processed Emails**: Reset tracking
- **Process Custom Batch**: Test with specific parameters
- **System Stats**: View detailed metrics

## 🚀 Advanced Usage

### **Email Provider Setup**

**Gmail:**
1. Enable 2FA
2. Generate App Password
3. Use App Password in EMAIL_PASSWORD

**Outlook:**
1. Enable IMAP in settings
2. Use regular password or App Password
3. Set EMAIL_IMAP_SERVER=outlook.office365.com

### **Webhook Integration**

```bash
# Test webhook
curl -X POST http://localhost:8000/webhook/email \
  -H "Content-Type: application/json" \
  -d '{"provider": "gmail", "event": "new_email"}'
```

## 📊 Performance & Scaling

### **Performance Metrics**
- **Real-time Processing**: <2 seconds from email arrival
- **Fallback Polling**: 5-minute intervals
- **AI Processing**: 1-5 seconds per email
- **Notion Creation**: 1-2 seconds per task

### **Scaling Considerations**
- **Email Volume**: Designed for personal/small team use
- **AI Rate Limits**: Automatic fallback between providers
- **Notion API**: Respects rate limits automatically
- **Memory Usage**: Minimal, suitable for always-on deployment

## 🛠️ Development

### **Project Structure**
```
AI-Agents-Swarm/
├── agents/                 # Core agent implementations
│   ├── core/              # Base classes and utilities
│   ├── email_polling/     # Email processing and real-time
│   ├── notion_integration/# Notion API integration
│   └── main.py           # Main orchestrator
├── api/                  # FastAPI server
├── config/               # Configuration management
├── ui/                   # Streamlit dashboard
├── tests/                # Test suites
├── docs/                 # Documentation
└── start.py              # Single command startup
```

### **Testing**
```bash
# Run all tests
python -m pytest tests/

# Test specific component
python tests/test_realtime_email.py

# System health check
python test_system.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [PydanticAI](https://github.com/pydantic/pydantic-ai) for AI model abstraction
- Uses [Streamlit](https://streamlit.io/) for the beautiful dashboard
- Powered by [FastAPI](https://fastapi.tiangolo.com/) for the robust API
- Integrates with [Notion](https://notion.so/) for task management

---

## 🎯 What's Next?

- 🔄 **Slack Integration**: Team notifications and commands
- 📱 **Mobile Dashboard**: Responsive design for mobile devices
- 🔍 **Advanced Search**: Full-text search across tasks and emails
- 🤖 **Custom AI Prompts**: User-configurable extraction rules
- 📊 **Analytics Dashboard**: Detailed insights and reporting
- 🔐 **Multi-user Support**: Team collaboration features

---

**Ready to transform your email workflow? Start with one command: `python start.py`** 🚀
