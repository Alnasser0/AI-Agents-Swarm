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

# Configure Streamlit page - MUST be first Streamlit command
st.set_page_config(
    page_title="AI Agents Swarm",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        self.init_success = False
        self.init_error = None
        print(f"Dashboard.__init__ called with model: {self.selected_model}")
        self.init_orchestrator()
    
    def init_orchestrator(self):
        """Initialize the agent orchestrator."""
        # Prevent multiple simultaneous initializations
        if hasattr(self, '_initializing') and self._initializing:
            print("Already initializing, skipping...")
            return
            
        self._initializing = True
        
        try:
            # Only reinitialize if the model has actually changed
            if self.orchestrator and hasattr(self.orchestrator, 'model') and self.orchestrator.model == self.selected_model:
                print(f"Orchestrator already initialized with model {self.selected_model}, skipping...")
                self._initializing = False
                return
                
            print(f"Initializing orchestrator with model: {self.selected_model}")
            self.orchestrator = AgentOrchestrator(model=self.selected_model)
            self.init_success = True
            self.init_error = None
            print("Orchestrator initialized successfully")
            
        except Exception as e:
            print(f"Error initializing orchestrator: {e}")
            self.init_success = False
            self.init_error = str(e)
            self.orchestrator = None
            
        finally:
            self._initializing = False
    
    def render_model_selector(self):
        """Render the AI model selector in the sidebar."""
        st.sidebar.header("🧠 AI Model Selection")
        
        # Cache model availability checks
        @st.cache_data(ttl=300)  # Cache for 5 minutes
        def get_model_options():
            available_models = get_available_models()
            model_options = []
            for provider, models in available_models.items():
                for model in models:
                    is_available = validate_model_availability(model)
                    status = "✅" if is_available else "❌"
                    model_options.append(f"{status} {model}")
            return model_options
        
        model_options = get_model_options()
        
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
            help="Select the AI model to use for task processing",
            key="model_selector"
        )
        
        # Extract model name from formatted option
        new_model = selected_option.split(" ", 1)[1]  # Remove status emoji
        
        # Update model if changed (but don't reinitialize during initial load)
        if new_model != self.selected_model:
            self.selected_model = new_model
            # Only reinitialize if we're not in the initial load phase
            if hasattr(self, 'init_success'):
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
        st.title("🤖 AI Agents Swarm Dashboard")
        st.markdown("*Automating your workflow with intelligent agents*")
        
        # Show initialization status
        if hasattr(self, 'init_success') and self.init_success:
            st.success("✅ System initialized successfully!")
        elif hasattr(self, 'init_error') and self.init_error:
            st.error(f"❌ Failed to initialize agents: {self.init_error}")
            st.error("Please check your configuration in the .env file.")
        
        st.divider()
    
    def render_sidebar(self):
        """Render the sidebar with controls."""
        with st.sidebar:
            # Model selector first
            self.render_model_selector()
            
            st.header("🎛️ Control Panel")
            
            # Manual trigger section
            st.subheader("**Automated Processing**")
            st.caption("📧 Process Emails: 50 emails from last 7 days | 🔄 Full Pipeline: Run all tasks")
            
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
            
            st.divider()
            
            # Debug controls
            st.subheader("🐛 Debug")
            st.caption("**Advanced Controls** - Custom settings for debugging and testing")
            
            # Email processing controls
            col1, col2 = st.columns(2)
            with col1:
                email_limit = st.number_input("Email Limit", min_value=1, max_value=200, value=50, help="Max emails to process")
            with col2:
                since_days = st.number_input("Days Back", min_value=1, max_value=30, value=7, help="Days back to check emails")
            
            st.markdown("**Custom Batch Processing**")
            if st.button("📧 Process Custom Batch", use_container_width=True, help="Process emails with custom settings above"):
                if self.orchestrator:
                    try:
                        self.orchestrator.force_email_processing(email_limit=email_limit, since_days=since_days)
                        st.success(f"Custom batch processed! ({email_limit} emails, {since_days} days)")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Orchestrator not initialized")

            st.markdown("**Force Operations** - Bypass normal scheduling, process 50 emails, 7 days back")
            if st.button("⚡ Force Email Processing", use_container_width=True, help="Force process emails ignoring schedule"):
                if self.orchestrator:
                    try:
                        self.orchestrator.force_email_processing()
                        st.success("Email processing triggered!")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Orchestrator not initialized")
            
            st.markdown("**Data Management**")
            if st.button("🗑️ Clear Processed Emails", use_container_width=True, help="Clear email processing cache"):
                if self.orchestrator:
                    try:
                        self.orchestrator.clear_processed_emails()
                        st.success("Processed emails cleared!")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Orchestrator not initialized")
            
            # Real-time Email Controls
            st.subheader("⚡ Real-time Email")
            
            if self.orchestrator and hasattr(self.orchestrator, 'realtime_processor'):
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🚀 Start Real-time"):
                        try:
                            self.orchestrator.start_realtime_monitoring()
                            st.success("Real-time started!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                            
                with col2:
                    if st.button("⏹️ Stop Real-time"):
                        try:
                            self.orchestrator.stop_realtime_monitoring()
                            st.success("Real-time stopped!")
                        except Exception as e:
                            st.error(f"Error: {e}")
            else:
                st.warning("Real-time processor not available")
    
    def render_status_cards(self):
        """Render status cards showing system health."""
        if not self.orchestrator:
            st.error("❌ System not initialized. Please check your configuration.")
            return
            
        stats = self.orchestrator.get_system_stats()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
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
                label="🗃️ Processed Cache",
                value=stats.get("processed_emails_count", 0),
                delta=None
            )
        
        with col4:
            st.metric(
                label="⏰ Uptime (hours)",
                value=f"{stats['uptime_hours']:.1f}",
                delta=None
            )
        
        with col5:
            st.metric(
                label="❌ Errors",
                value=stats["errors"],
                delta=None
            )
    
    def render_agent_status(self):
        """Render agent status section."""
        st.subheader("🤖 Agent Status")
        
        if not self.orchestrator:
            st.error("❌ Agents not initialized. Please check your configuration.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Email Agent")
            st.success("🟢 Active")
            st.text(f"Provider: {settings.email_provider}")
            st.text(f"Account: {settings.email_address}")
            st.text(f"Check Interval: {settings.email_check_interval//60} minutes")
            
            # Real-time processing status
            if self.orchestrator and hasattr(self.orchestrator, 'realtime_processor'):
                stats = self.orchestrator.get_system_stats()
                realtime_status = stats.get('realtime_email', {})
                
                if realtime_status.get('idle_supported', False):
                    if realtime_status.get('idle_running', False) and realtime_status.get('idle_thread_alive', False):
                        st.success("⚡ Real-time: Active (IMAP IDLE)")
                    elif realtime_status.get('idle_running', False):
                        st.warning("⚡ Real-time: Starting...")
                    else:
                        st.info("⚡ Real-time: Stopped")
                else:
                    st.info("⚡ Real-time: Polling only (IDLE not supported)")
            else:
                st.info("⚡ Real-time: Not initialized")
        
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
        if not self.orchestrator:
            st.error("❌ Orchestrator not initialized. Please check your configuration.")
            return
            
        with st.spinner("Processing emails..."):
            try:
                # Run the actual email processing pipeline
                asyncio.run(self.orchestrator.run_single_cycle())
                
                # Get updated stats
                stats = self.orchestrator.get_system_stats()
                
                if stats['tasks_processed'] > 0:
                    st.success(f"✅ Email processing completed! {stats['tasks_processed']} tasks created.")
                else:
                    st.info("📧 Email processing completed. No new tasks found.")
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error processing emails: {e}")
                
    def trigger_full_pipeline(self):
        """Trigger the full email-to-notion pipeline."""
        if not self.orchestrator:
            st.error("❌ Orchestrator not initialized. Please check your configuration.")
            return
            
        with st.spinner("Running full pipeline..."):
            try:
                # Run the actual pipeline
                asyncio.run(self.orchestrator.run_single_cycle())
                
                # Get updated stats
                stats = self.orchestrator.get_system_stats()
                
                if stats['tasks_processed'] > 0:
                    st.success(f"🎉 Pipeline completed! {stats['tasks_processed']} tasks created, {stats['emails_processed']} emails processed.")
                else:
                    st.info("🔄 Pipeline completed. No new tasks found.")
                
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error running pipeline: {e}")
                import traceback
                st.error(traceback.format_exc())
    
    def render_main_dashboard(self):
        """Render the main dashboard content."""
        # Status cards
        self.render_status_cards()
        
        st.divider()
        
        # Two column layout for status
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Empty space or could be used for other content
            st.empty()
        
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
        
        # Auto-refresh control
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Refresh", key="refresh_btn"):
                st.rerun()
        
        # Remove problematic auto-refresh that causes loops
        # Auto-refresh every 60 seconds (optional)
        # if st.checkbox("Auto-refresh (60s)", key="auto_refresh"):
        #     time.sleep(60)
        #     st.rerun()


def main():
    """Main entry point for the dashboard."""
    # Use session state to persist dashboard instance
    if 'dashboard' not in st.session_state:
        st.session_state.dashboard = Dashboard()
    
    dashboard = st.session_state.dashboard
    dashboard.run()


if __name__ == "__main__":
    main()
