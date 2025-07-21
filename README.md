# 🤖 AI Agents Swarm

A powerful, intelligent automation system that transforms your email inbox into a smart task management workflow. Built with modern AI agents that work together to extract, process, and organize actionable tasks automatically from your email communications.

## 🌟 High-level overview:

### **Intelligent Email Processing**
- **Automatic Monitoring**: Continuously watches your mail inbox for new messages
- **Smart Task Extraction**: Uses AI to identify actionable items from emails
- **Zero Manual Processing**: Tasks appear in their own business apps without any manual effort

### **Key Features**

- **Real-time Email Processing**: IMAP IDLE for instant task creation
- **Docker Deployment**: execute 1 line to run the whole app
- **Automatic Fallback**: Robust polling-mode if real-time fails
- **Duplicate Prevention**: Smart detection prevents processing same email twice
- **Multi-Model Support**: OpenAI GPT, Anthropic Claude, Google Gemini
- **Dynamic AI Fallback**: Automatically switches between AI providers
- **REST API**: Full programmatic control and monitoring
- **System Health Monitoring**: Comprehensive diagnostics and alerts

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+ (3.11 recommended)
- Node.js 18+ (for React dashboard)
- Gmail account with 2FA enabled
- Notion account with integration setup
- Setting the .env file, copy and edit .env.example.

### **Docker Deployment (Recommended)**

```bash
# One command for production deployment
docker-compose up --build
```

### **Complete Setup (Not Recommended, use Docker)**

```bash
# 1. Clone and enter directory
git clone https://github.com/yourusername/AI-Agents-Swarm.git
cd AI-Agents-Swarm

# 2. Run comprehensive setup script
python setup.py

# 3. Run the app
python start.py
```

### **What Happens When You Start**

The system automatically:
- 🌐 Starts FastAPI server at http://localhost:8000
- 📊 Launches React dashboard at http://localhost:3000  
- 📧 Begins real-time email monitoring
- 🔗 Opens browser to dashboard
- 📝 Starts monitoring emails and creating Notion tasks

### **Accessing the System**

- **Dashboard**: http://localhost:3000 (Primary interface)
- **API**: http://localhost:8000/
- **Health Check**: http://localhost:8000/health (System status)
- **Logs**: Check `logs/` directory for detailed logging

## ⚠️ Important Setup Notes

### **Gmail Configuration (Required)**
1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**: Google Account → Security → App Passwords
3. **Use App Password** in `EMAIL_PASSWORD` (not your regular password)
4. **IMAP must be enabled** (usually enabled by default)

### **Notion Setup (Required)**
1. **Create Integration**: https://notion.so/integrations → New Integration
2. **Get API Key**: Copy the integration token
3. **Create Database**: Create a new database in Notion
4. **Share Database**: Share the database with your integration
5. **Get Database ID**: Copy from database URL

### **Add Your AI Model API to .env (Required)**
- **Gemini (Recommended)**: Get API key from Google AI Studio - **tested**
- **OpenAI**: Get API key from OpenAI dashboard - **Not tested**  
- **Anthropic**: Get API key from Anthropic console - **Not tested**

## **Project Structure**
```
AI-Agents-Swarm/
├── agents/                    # Core agent implementations
│   ├── core/                 # Base classes and AI models
│   ├── email_polling/        # Email processing and monitoring
│   ├── notion_integration/   # Notion API integration
│   └── main.py              # Agent orchestrator
├── api/                      # FastAPI REST server
│   └── server.py              # FastAPI application
├── dashboard-react/          # Next.js React dashboard
│   ├── src/components/      # React components
│   └── src/hooks/          # Custom React hooks
├── config/                   # Configuration management
│   ├── settings.py         # Environment variable handling
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Production deployment
├── setup.py                # Automated setup script
└── start.py                # Development startup script
```

## � Acknowledgments

### **Core Technologies**
- **[PydanticAI](https://github.com/pydantic/pydantic-ai)**: Modern AI framework for structured model interactions
- **[FastAPI](https://fastapi.tiangolo.com/)**: High-performance API framework with automatic documentation
- **[Next.js](https://nextjs.org/)**: React framework for production-ready web applications

## 🎯 What's Next?

### **Planned Features**
- 🔄 **Communication app Integration**: Meetings summary, Communication summary, tasks summary, etc.
- 📅 **Calendar Integration**: Automatic calendar event creation and management