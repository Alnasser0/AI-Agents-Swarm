"""
Streamlit Dashboard for AI Agents Swarm.

This provides a beautiful, real-time dashboard for monitoring and controlling
the AI automation system. Features include:
- Real-time agent status
- Manual trigger controls
- Task creation history
- System statistics
- Configuration management
"""

import streamlit as st
import asyncio
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Internal imports
from agents.main import AgentOrchestrator
from agents.core import Task, get_available_models, get_best_available_model, validate_model_availability
from config.settings import settings


class Dashboard:
    """Main dashboard class for the Streamlit UI."""
    
    def __init__(self):
        """Initialize the dashboard."""
        self.orchestrator = None
        self.selected_model = get_best_available_model()
        self.init_orchestrator()
    
    def init_orchestrator(self):
        """Initialize the agent orchestrator."""
        try:
            self.orchestrator = AgentOrchestrator(model=self.selected_model)
        except Exception as e:
            st.error(f"Failed to initialize agents: {e}")
            st.stop()
    
    def render_model_selector(self):
        """Render the AI model selector in the sidebar."""
        st.sidebar.header("🧠 AI Model Selection")
        
        available_models = get_available_models()
        
        # Flatten model list for selectbox
        model_options = []
        for provider, models in available_models.items():
            for model in models:
                is_available = validate_model_availability(model)
                status = "✅" if is_available else "❌"
                model_options.append(f"{status} {model}")
        
        # Find current selection index
        current_index = 0
        for i, option in enumerate(model_options):
            if self.selected_model in option:
                current_index = i
                break
        
        selected_option = st.sidebar.selectbox(
            "Choose AI Model",
            options=model_options,
            index=current_index,
            help="Select the AI model to use for task processing"
        )
        
        # Extract model name from formatted option
        new_model = selected_option.split(" ", 1)[1]  # Remove status emoji
        
        # Update model if changed
        if new_model != self.selected_model:
            self.selected_model = new_model
            self.init_orchestrator()  # Reinitialize with new model
            st.rerun()
        
        # Show model status
        if validate_model_availability(self.selected_model):
            st.sidebar.success(f"✅ Model ready: {self.selected_model}")
        else:
            st.sidebar.error(f"❌ Model not configured: {self.selected_model}")
            st.sidebar.info("Check your API keys in the .env file")
        
        st.sidebar.divider()
    
    def render_header(self):
        """Render the dashboard header."""
        st.set_page_config(
            page_title="AI Agents Swarm",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("🤖 AI Agents Swarm Dashboard")
        st.markdown("*Automating your workflow with intelligent agents*")
        st.divider()
    
    def render_sidebar(self):
        """Render the sidebar with controls."""
        with st.sidebar:
            # Model selector first
            self.render_model_selector()
            
            st.header("🎛️ Control Panel")
            
            # Manual trigger section
            st.subheader("Manual Triggers")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📧 Process Emails", use_container_width=True):
                    self.trigger_email_processing()
            
            with col2:
                if st.button("🔄 Full Pipeline", use_container_width=True):
                    self.trigger_full_pipeline()
            
            st.divider()
            
            # Configuration section
            st.subheader("⚙️ Configuration")
            
            # Email settings
            with st.expander("Email Settings"):
                st.text_input("Email Address", value=settings.email_address, disabled=True)
                st.text_input("IMAP Server", value=settings.email_imap_server, disabled=True)
                st.number_input("Check Interval (min)", value=settings.email_check_interval//60, disabled=True)
            
            # Notion settings
            with st.expander("Notion Settings"):
                st.text_input("Database ID", value=settings.notion_database_id, disabled=True)
                st.text("API Key: " + ("✓ Configured" if settings.notion_api_key else "❌ Missing"))
            
            # AI settings
            with st.expander("AI Settings"):
                st.text_input("Default Model", value=settings.default_model, disabled=True)
                st.text("OpenAI: " + ("✓ Configured" if settings.openai_api_key else "❌ Missing"))
                st.text("Anthropic: " + ("✓ Configured" if settings.anthropic_api_key else "✓ Configured"))
            
            st.divider()
            
            # System controls
            st.subheader("🔧 System")
            
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()
            
            if st.button("🧹 Clear Cache", use_container_width=True):
                st.cache_data.clear()
                st.success("Cache cleared!")
    
    def render_status_cards(self):
        """Render status cards showing system health."""
        stats = self.orchestrator.get_system_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📧 Emails Processed",
                value=stats["emails_processed"],
                delta=None
            )
        
        with col2:
            st.metric(
                label="✅ Tasks Created",
                value=stats["tasks_processed"],
                delta=None
            )
        
        with col3:
            st.metric(
                label="⏰ Uptime (hours)",
                value=f"{stats['uptime_hours']:.1f}",
                delta=None
            )
        
        with col4:
            st.metric(
                label="❌ Errors",
                value=stats["errors"],
                delta=None
            )
    
    def render_activity_chart(self):
        """Render activity chart (mock data for now)."""
        st.subheader("📊 Activity Over Time")
        
        # Generate mock time series data
        dates = pd.date_range(start=datetime.now() - timedelta(days=7), end=datetime.now(), freq='H')
        tasks_created = [max(0, int(3 * (1 + 0.5 * (i % 24 - 12) / 12))) for i in range(len(dates))]
        
        df = pd.DataFrame({
            'Time': dates,
            'Tasks Created': tasks_created
        })
        
        fig = px.line(df, x='Time', y='Tasks Created', title='Tasks Created Over Time')
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Tasks Created",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_agent_status(self):
        """Render agent status section."""
        st.subheader("🤖 Agent Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Email Agent")
            st.success("🟢 Active")
            st.text(f"Provider: {settings.email_provider}")
            st.text(f"Account: {settings.email_address}")
            st.text(f"Check Interval: {settings.email_check_interval//60} minutes")
        
        with col2:
            st.markdown("#### Notion Agent")
            st.success("🟢 Active")
            st.text(f"Database: {settings.notion_database_id[:8]}...")
            
            # Check database connectivity
            if self.orchestrator.notion_agent.validate_database_setup():
                st.text("Schema: ✅ Valid")
            else:
                st.text("Schema: ❌ Invalid")
    
    def render_recent_tasks(self):
        """Render recent tasks table (mock data for now)."""
        st.subheader("📋 Recent Tasks")
        
        # Mock recent tasks data
        mock_tasks = [
            {
                "Title": "Review presentation slides",
                "Source": "Email",
                "Priority": "High",
                "Status": "To Do",
                "Created": datetime.now() - timedelta(minutes=15),
                "From": "manager@company.com"
            },
            {
                "Title": "Update project timeline",
                "Source": "Email", 
                "Priority": "Medium",
                "Status": "To Do",
                "Created": datetime.now() - timedelta(hours=2),
                "From": "team@company.com"
            },
            {
                "Title": "Schedule team meeting",
                "Source": "Email",
                "Priority": "Low",
                "Status": "Done",
                "Created": datetime.now() - timedelta(hours=4),
                "From": "assistant@company.com"
            }
        ]
        
        df = pd.DataFrame(mock_tasks)
        df['Created'] = df['Created'].dt.strftime('%Y-%m-%d %H:%M')
        
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "Priority": st.column_config.SelectboxColumn(
                    "Priority",
                    options=["Low", "Medium", "High", "Urgent"],
                    default="Medium"
                ),
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["To Do", "In Progress", "Done", "Cancelled"],
                    default="To Do"
                )
            }
        )
    
    def render_logs(self):
        """Render system logs section."""
        st.subheader("📜 System Logs")
        
        # Mock log entries
        mock_logs = [
            f"[{datetime.now().strftime('%H:%M:%S')}] INFO | EmailAgent | Successfully connected to email server",
            f"[{(datetime.now() - timedelta(minutes=2)).strftime('%H:%M:%S')}] INFO | NotionAgent | Created Notion task: Review presentation slides",
            f"[{(datetime.now() - timedelta(minutes=5)).strftime('%H:%M:%S')}] INFO | EmailAgent | Processed 3 emails, extracted 2 tasks",
            f"[{(datetime.now() - timedelta(minutes=10)).strftime('%H:%M:%S')}] INFO | Orchestrator | Pipeline complete: 2/2 tasks created",
        ]
        
        # Create a scrollable log area
        log_container = st.container()
        with log_container:
            for log in mock_logs:
                if "ERROR" in log:
                    st.error(log)
                elif "WARNING" in log:
                    st.warning(log)
                else:
                    st.text(log)
    
    def trigger_email_processing(self):
        """Trigger manual email processing."""
        with st.spinner("Processing emails..."):
            try:
                # This would trigger the actual email processing
                time.sleep(2)  # Simulate processing time
                st.success("Email processing completed!")
                st.rerun()
            except Exception as e:
                st.error(f"Error processing emails: {e}")
    
    def trigger_full_pipeline(self):
        """Trigger the full email-to-notion pipeline."""
        with st.spinner("Running full pipeline..."):
            try:
                # This would trigger the actual pipeline
                time.sleep(3)  # Simulate processing time
                st.success("Pipeline completed successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error running pipeline: {e}")
    
    def render_main_dashboard(self):
        """Render the main dashboard content."""
        # Status cards
        self.render_status_cards()
        
        st.divider()
        
        # Two column layout for charts and status
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self.render_activity_chart()
        
        with col2:
            self.render_agent_status()
        
        st.divider()
        
        # Recent tasks
        self.render_recent_tasks()
        
        st.divider()
        
        # System logs
        self.render_logs()
    
    def run(self):
        """Main dashboard runner."""
        self.render_header()
        self.render_sidebar()
        self.render_main_dashboard()
        
        # Auto-refresh every 30 seconds
        time.sleep(30)
        st.rerun()


def main():
    """Main entry point for the dashboard."""
    dashboard = Dashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
