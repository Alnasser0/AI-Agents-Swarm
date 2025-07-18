# 🤖 AI Agents Swarm

> **Modular AI automation system for solo developers**

A production-ready automation system that automates repetitive business tasks using AI agents. Built with modularity and extensibility in mind.

## ✨ Features

- **Email-to-Notion**: Automatically process and categorize emails into Notion databases
- **Slack Summarization**: Generate daily/weekly summaries of important conversations
- **Multi-Model Support**: OpenAI, Anthropic Claude, Google Gemini
- **Extensible Architecture**: Easy to add new agents and integrations
- **Modern Stack**: Pydantic-AI, LangGraph, FastAPI, Streamlit

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the system**:
   ```bash
   python -m agents.main
   ```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# AI Model Configuration
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GEMINI_API_KEY=your-gemini-key

# Email Configuration (Gmail)
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-gmail-app-password  # Use Gmail App Password, not regular password
EMAIL_IMAP_SERVER=imap.gmail.com
EMAIL_IMAP_PORT=993

# Notion Configuration
NOTION_TOKEN=your-notion-integration-token
NOTION_DATABASE_ID=your-database-id

# Slack Configuration (optional)
SLACK_TOKEN=your-slack-token
```

### 📧 Gmail App Password Setup

For secure email access, use Gmail App Passwords instead of your regular password:

1. **Enable 2-Factor Authentication** on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an App Password for "Mail"
4. Use this 16-character password in your `.env` file

This is more secure than using your regular password and won't be stored in plain text.

## 📁 Project Structure

```
AI-Agents-Swarm/
├── agents/
│   ├── core/           # Core agent functionality
│   ├── email/          # Email processing agents
│   ├── notion/         # Notion integration
│   └── slack/          # Slack integration
├── config/             # Configuration management
├── utils/              # Shared utilities
├── examples/           # Example scripts
├── docs/               # Documentation
└── tests/              # Test suites
```

## 🔄 Available Agents

### 1. Email-to-Notion Agent
- Processes incoming emails
- Extracts key information using AI
- Creates structured Notion entries
- Supports custom categorization

### 2. Slack Summary Agent
- Monitors Slack channels
- Generates daily/weekly summaries
- Identifies important conversations
- Sends summary notifications

### 3. Content Processor Agent
- Processes various content types
- Extracts insights and actions
- Integrates with external systems
- Supports custom workflows

## 🛠️ Development

### Adding New Agents

1. Create a new module in `agents/`
2. Implement the `BaseAgent` interface
3. Add configuration to `config/settings.py`
4. Register in `agents/__init__.py`

### Example Agent Structure

```python
from agents.core.base import BaseAgent
from pydantic import BaseModel

class MyAgent(BaseAgent):
    async def process(self, input_data: BaseModel) -> BaseModel:
        # Your agent logic here
        return output_data
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# Run specific test suite
python -m pytest tests/test_email_agent.py

# Run with coverage
python -m pytest --cov=agents
```

## 🌐 Web Interface

Access the Streamlit dashboard:

```bash
streamlit run dashboard/app.py
```

## 📚 Documentation

- [Agent Development Guide](docs/agent-development.md)
- [Configuration Reference](docs/configuration.md)
- [API Documentation](docs/api.md)
- [Deployment Guide](docs/deployment.md)

## 🔧 Environment Setup

### Prerequisites

- Python 3.9+
- pip or poetry
- Gmail account with App Password
- Notion workspace with integration

### Installation

```bash
git clone https://github.com/yourusername/AI-Agents-Swarm.git
cd AI-Agents-Swarm
pip install -r requirements.txt
```

## 📊 Monitoring

The system includes built-in monitoring:

- **Logging**: Structured logging with loguru
- **Metrics**: Performance and usage metrics
- **Health Checks**: System health monitoring
- **Alerts**: Error and performance alerts

## 🚀 Deployment

### Docker

```bash
# Build image
docker build -t ai-agents-swarm .

# Run container
docker run -d --env-file .env ai-agents-swarm
```

### Production

See [Deployment Guide](docs/deployment.md) for production setup instructions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- Create an issue for bugs or feature requests
- Check the [documentation](docs/) for detailed guides
- Join our community discussions

---
