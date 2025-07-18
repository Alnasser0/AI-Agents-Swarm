"""
CLI utilities for AI Agents Swarm.

This module provides command-line interface utilities for managing
and interacting with the agent system.
"""

import click
import asyncio
from typing import Optional
from datetime import datetime

# Internal imports
from agents.main import AgentOrchestrator
from agents.core import get_available_models, get_best_available_model, validate_model_availability
from config.settings import settings


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """AI Agents Swarm CLI - Automate your workflow with intelligent agents."""
    pass


@cli.command()
@click.option("--background", "-b", is_flag=True, help="Run in background mode")
@click.option("--once", "-o", is_flag=True, help="Run once and exit")
@click.option("--model", "-m", help="AI model to use (e.g., 'openai:gpt-4o', 'anthropic:claude-3-5-sonnet-latest', 'google-gla:gemini-2.0-flash')")
def run(background: bool, once: bool, model: Optional[str]):
    """Start the agent system."""
    
    # Validate model if specified
    if model:
        if not validate_model_availability(model):
            click.echo(f"⚠️  Warning: Model {model} may not be properly configured")
            click.echo("Please check your API keys in the .env file")
    
    # Use best available model if none specified
    selected_model = model or get_best_available_model()
    
    click.echo("🤖 Starting AI Agents Swarm...")
    click.echo(f"🧠 Using model: {selected_model}")
    
    try:
        orchestrator = AgentOrchestrator(model=selected_model)
        
        if once:
            click.echo("Running single cycle...")
            asyncio.run(orchestrator.run_interactive_mode())
            click.echo("✅ Single cycle completed")
            
        elif background:
            click.echo("Starting background mode...")
            orchestrator.run_background_mode()
            
        else:
            click.echo("Starting interactive mode...")
            asyncio.run(orchestrator.run_interactive_mode())
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
def models():
    """List available AI models."""
    click.echo("🧠 Available AI Models:")
    
    available_models = get_available_models()
    best_model = get_best_available_model()
    
    for provider, model_list in available_models.items():
        click.echo(f"\n📚 {provider.title()} Models:")
        
        for model in model_list:
            # Check if model is available
            is_available = validate_model_availability(model)
            status = "✅" if is_available else "❌"
            
            marker = ""
            if model == best_model:
                marker = " (⭐ best available)"
            elif not is_available:
                marker = " (check API keys)"
            
            click.echo(f"  {status} {model}{marker}")
    
    click.echo(f"\n🌟 Best available model: {best_model}")
    click.echo("\nTo use a specific model, run: python cli.py run --model MODEL_NAME")


@cli.command()
def status():
    """Show system status."""
    click.echo("🔍 Checking system status...")
    
    try:
        orchestrator = AgentOrchestrator()
        stats = orchestrator.get_system_stats()
        
        click.echo("\n📊 System Statistics:")
        click.echo(f"  Tasks Processed: {stats['tasks_processed']}")
        click.echo(f"  Emails Processed: {stats['emails_processed']}")
        click.echo(f"  Errors: {stats['errors']}")
        click.echo(f"  Uptime: {stats['uptime_hours']:.1f} hours")
        
        if stats['last_run']:
            click.echo(f"  Last Run: {stats['last_run']}")
        
        click.echo("\n🤖 Agent Status:")
        click.echo(f"  Email Agent: {stats['email_agent_status']}")
        click.echo(f"  Notion Agent: {stats['notion_agent_status']}")
        
    except Exception as e:
        click.echo(f"❌ Error getting status: {e}", err=True)
        raise click.Abort()


@cli.command()
def test():
    """Test system connectivity."""
    click.echo("🧪 Testing system connectivity...")
    
    try:
        orchestrator = AgentOrchestrator()
        
        # Test email connectivity
        click.echo("Testing email connection...")
        try:
            mail = orchestrator.email_agent.connect_to_email()
            mail.close()
            click.echo("✅ Email connection successful")
        except Exception as e:
            click.echo(f"❌ Email connection failed: {e}")
        
        # Test Notion connectivity
        click.echo("Testing Notion connection...")
        if orchestrator.notion_agent.validate_database_setup():
            click.echo("✅ Notion connection successful")
        else:
            click.echo("❌ Notion connection failed")
        
    except Exception as e:
        click.echo(f"❌ Error during testing: {e}", err=True)
        raise click.Abort()


@cli.command()
def config():
    """Show current configuration."""
    click.echo("⚙️ Current Configuration:")
    click.echo(f"  Email Provider: {settings.email_provider}")
    click.echo(f"  Email Address: {settings.email_address}")
    click.echo(f"  IMAP Server: {settings.email_imap_server}")
    click.echo(f"  Check Interval: {settings.email_check_interval} seconds")
    click.echo(f"  Default Model: {settings.default_model}")
    click.echo(f"  Background Tasks: {settings.enable_background_tasks}")
    click.echo(f"  Log Level: {settings.log_level}")


@cli.command()
@click.option("--title", "-t", required=True, help="Task title")
@click.option("--description", "-d", default="", help="Task description")
@click.option("--priority", "-p", default="medium", help="Task priority")
def create_task(title: str, description: str, priority: str):
    """Create a task manually."""
    click.echo(f"📝 Creating task: {title}")
    
    try:
        from agents.core import Task, TaskPriority
        
        # Map priority string to enum
        priority_map = {
            "low": TaskPriority.LOW,
            "medium": TaskPriority.MEDIUM,
            "high": TaskPriority.HIGH,
            "urgent": TaskPriority.URGENT
        }
        
        task_priority = priority_map.get(priority.lower(), TaskPriority.MEDIUM)
        
        orchestrator = AgentOrchestrator()
        
        task = Task(
            title=title,
            description=description,
            priority=task_priority,
            source="cli",
            metadata={"created_via": "cli"}
        )
        
        page_id = orchestrator.notion_agent.create_task_in_notion(task)
        
        if page_id:
            click.echo(f"✅ Task created successfully (ID: {page_id})")
        else:
            click.echo("❌ Failed to create task")
            
    except Exception as e:
        click.echo(f"❌ Error creating task: {e}", err=True)
        raise click.Abort()


@cli.command()
def dashboard():
    """Launch the Streamlit dashboard."""
    click.echo("🚀 Launching dashboard...")
    
    import subprocess
    import sys
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "ui/dashboard.py",
            "--server.port", str(settings.dashboard_port),
            "--server.address", settings.dashboard_host
        ])
    except KeyboardInterrupt:
        click.echo("\n👋 Dashboard stopped")
    except Exception as e:
        click.echo(f"❌ Error launching dashboard: {e}", err=True)


@cli.command()
def api():
    """Launch the API server."""
    click.echo("🌐 Launching API server...")
    
    try:
        from api.server import run_server
        run_server()
    except KeyboardInterrupt:
        click.echo("\n👋 API server stopped")
    except Exception as e:
        click.echo(f"❌ Error launching API server: {e}", err=True)


@cli.command()
def logs():
    """Show recent logs."""
    click.echo("📜 Recent logs:")
    
    try:
        import os
        log_file = "logs/agents.log"
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                # Show last 20 lines
                for line in lines[-20:]:
                    click.echo(line.strip())
        else:
            click.echo("No log file found")
            
    except Exception as e:
        click.echo(f"❌ Error reading logs: {e}", err=True)


if __name__ == "__main__":
    cli()
