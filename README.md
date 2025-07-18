# AI-Agents-Swarm 🤖

A **minimalist AI automation system** for solo developers to automate simple business tasks with zero friction.

## 🎯 Current Features

- **Email-to-Notion**: Automatically convert task emails into Notion tasks
- **Slack Summarization**: Summarize Slack messages (coming soon)
- **Clean Architecture**: Modular monolith with 1-3 files per feature
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

4. **Open the UI**:
   ```bash
   streamlit run ui/dashboard.py
   ```

## 📁 Architecture

```
agents/
├── email_polling/          # Email integration (IMAP + Gmail)
├── notion_integration/     # Notion API wrapper
├── slack_integration/      # Slack API wrapper (future)
├── core/                   # Shared utilities and agents
├── main.py                 # Application entry point
ui/
├── dashboard.py            # Streamlit dashboard
config/
├── settings.py             # Configuration management
```

## 🔧 Configuration

All configuration is handled through `.env` files:

```bash
# Email
EMAIL_PROVIDER=gmail
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# Notion
NOTION_API_KEY=your-notion-key
NOTION_DATABASE_ID=your-database-id

# AI
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

## 🧩 Adding New Integrations

To add a new integration (e.g., `calendar_sync`):

1. Create `agents/calendar_sync/` folder
2. Add `__init__.py` and `calendar_agent.py`
3. Register in `agents/main.py`

That's it! The system is designed for minimal friction.

## 📊 Usage Examples

### Email-to-Notion
```python
# Automatic polling every 5 minutes
# Converts emails like "Create task: Review presentation" 
# Into Notion tasks with proper metadata
```

### Manual Trigger
```python
from agents.email_polling import EmailAgent

agent = EmailAgent()
tasks = agent.process_new_emails()
print(f"Created {len(tasks)} new tasks")
```

## 🎨 UI Dashboard

The Streamlit dashboard provides:
- Real-time agent status
- Manual trigger controls
- Task creation history
- Configuration management

## 🔮 Future Extensions

- Jira integration
- Calendar automation
- Document processing
- Custom workflows

## 📝 License

MIT License - Build amazing things!