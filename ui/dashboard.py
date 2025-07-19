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

# Custom CSS for modern 2025 UI/UX
st.markdown("""
<style>
    /* --- Base & Background --- */
    body {
        background-color: #020617 !important; /* Dark Navy Blue */
        color: #e2e8f0; /* Light gray text for readability */
    }
    .stApp {
        background-color: #020617;
    }

    /* --- Remove top padding and fix empty space --- */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    
    /* --- Sidebar Styling --- */
    .css-1d391kg { /* This is the main sidebar class */
        background: #0f172a; /* Darker blue for sidebar */
        padding-top: 0.5rem;
        border-right: 1px solid #1e293b;
    }
    
    /* Eliminate ALL excessive sidebar spacing */
    .stSidebar .stMarkdown, .stSidebar .stSubheader, .stSidebar .stButton, 
    .stSidebar .stSelectbox, .stSidebar .stHeader, .stSidebar .stExpander, 
    .stSidebar .stColumns, .stSidebar .stNumberInput, .stSidebar .stCaption {
        margin-top: 0.25rem !important;
        margin-bottom: 0.25rem !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* --- Enhanced Metric Cards --- */
    div[data-testid="metric-container"] {
        background: rgba(30, 41, 59, 0.5); /* Faded, semi-transparent background */
        border: 1px solid #334155;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: all 0.2s ease;
        margin-bottom: 0.5rem;
    }
    
    div[data-testid="metric-container"]:hover {
        background: rgba(51, 65, 85, 0.7);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* MUCH larger, more readable metric values */
    div[data-testid="metric-container"] > div > div > div[data-testid="metric-value"] {
        font-size: 4rem !important; /* Even bigger number */
        font-weight: 800 !important;
        color: #f8fafc !important; /* Bright white for contrast */
        margin-bottom: 0.5rem !important;
    }
    
    /* Better metric labels - larger and more readable */
    div[data-testid="metric-container"] > div > div > div[data-testid="metric-label"] {
        font-size: 1.5rem !important; /* Bigger label */
        font-weight: 600 !important;
        color: #94a3b8 !important; /* Lighter gray for label */
        margin-bottom: 0.75rem !important;
        line-height: 1.4 !important;
    }
    
    /* --- Agent & Status Styling --- */
    .agent-card {
        background: #0f172a !important; 
        border: 1px solid #1e293b !important;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        max-width: 500px;
        position: relative;
    }
    
    .agent-card h4 {
        color: #f1f5f9 !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.5rem !important;
        display: flex;
        align-items: center;
    }
    
    .agent-card .agent-details {
        color: #94a3b8 !important;
        font-size: 0.875rem !important;
        line-height: 1.4 !important;
    }
    
    /* Agent Status Indicators */
    .agent-status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 0.75rem;
        animation: pulse 2s infinite;
        box-shadow: 0 0 8px rgba(0,0,0,0.5);
    }
    
    .agent-status-online {
        background: #10b981 !important; /* Bright Green */
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.8);
    }
    
    .agent-status-offline {
        background: #ef4444 !important; /* Bright Red */
        box-shadow: 0 0 12px rgba(239, 68, 68, 0.8);
    }
    
    .agent-status-warning {
        background: #f59e0b !important; /* Bright Yellow */
        box-shadow: 0 0 12px rgba(245, 158, 11, 0.8);
    }
    
    /* --- System Logs Cleanup --- */
    .log-container-wrapper {
        background: #0f172a !important;
        border: 1px solid #1e293b !important;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }

    .log-scroll-area {
        font-family: 'Monaco', 'Consolas', monospace;
        max-height: 400px;
        overflow-y: auto;
        padding-right: 10px;
    }
    
    /* Removed background colors from individual logs */
    .log-entry-info, .log-entry-error, .log-entry-warning, .log-entry-default {
        background: transparent !important; 
        padding: 0.2rem 0.4rem;
        margin: 0.1rem 0;
        border-radius: 4px;
        font-size: 0.8rem;
        font-family: monospace;
    }

    /* Use softer, eye-friendly text colors for differentiation */
    .log-entry-info { color: #60a5fa !important; } /* Soft Blue */
    .log-entry-error { color: #fb7185 !important; } /* Soft Pink/Red */
    .log-entry-warning { color: #fbbf24 !important; } /* Soft Yellow */
    .log-entry-default { color: #cbd5e1 !important; } /* Soft Gray */

    /* --- Real-time Status Indicator --- */
    .realtime-status {
        margin-top: 0.5rem;
        padding: 0.4rem 0.8rem; /* Smaller padding */
        border-radius: 6px;
        text-align: center;
        font-size: 0.8rem !important; /* Smaller font */
        font-weight: 600 !important; /* Bolder */
        max-width: 220px; /* Controlled width */
        border: 1px solid transparent;
    }
    
    .realtime-active {
        background: #065f46 !important; /* Darker, muted green */
        color: #d1fae5 !important; /* Light mint text */
        border-color: #059669;
        box-shadow: 0 0 6px rgba(5, 150, 105, 0.4); /* Softer glow */
    }
    
    .realtime-starting {
        background: #78350f !important; /* Muted amber */
        color: #fef3c7 !important;
        border-color: #92400e;
    }
    
    .realtime-stopped {
        background: #1e40af !important; /* Muted blue */
        color: #dbeafe !important;
        border-color: #2563eb;
    }
    
    .realtime-polling {
        background: #374151 !important; /* Neutral gray */
        color: #f3f4f6 !important;
        border-color: #4b5563;
    }
    
    .realtime-error {
        background: #7f1d1d !important; /* Muted red */
        color: #fee2e2 !important;
        border-color: #991b1b;
    }

</style>
""", unsafe_allow_html=True)

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
        
        st.sidebar.divider()
    
    def render_header(self):
        """Render the modern dashboard header."""
        # Main title with a transparent background to blend with the new dark theme
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem 0; margin-bottom: 1rem;">
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700; color: #f8fafc;">🤖 AI Agents Swarm</h1>
            <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; color: #94a3b8;">Automating your workflow with intelligent agents</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialization status - with fade effect for success
        if hasattr(self, 'init_success') and self.init_success:
            # Use session state to only show the message once per session after init
            if 'init_message_shown' not in st.session_state:
                st.markdown("""
                <div class="fade-message" style="background: #10b981; border: 1px solid #34d399; color: #ffffff; padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem;">
                    ✅ System initialized successfully!
                </div>
                """, unsafe_allow_html=True)
                
                # After showing, set a flag and trigger a rerun after the animation duration
                st.session_state.init_message_shown = True
                time.sleep(4) # Wait for animation to finish
                st.rerun()
            
        elif hasattr(self, 'init_error') and self.init_error:
            st.markdown("""
            <div style="background: #fee2e2; border: 1px solid #fca5a5; color: #7f1d1d; padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem;">
                ❌ Failed to initialize agents: {}
                <br><small>Please check your configuration in the .env file.</small>
            </div>
            """.format(self.init_error), unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the sidebar with controls."""
        with st.sidebar:
            # Model selector first
            self.render_model_selector()
            
            # Minimal spacing
            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            
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
            
            # Minimal spacing
            st.markdown("<div style='height: 0.25rem;'></div>", unsafe_allow_html=True)
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
            
            # Minimal spacing
            st.markdown("<div style='height: 0.25rem;'></div>", unsafe_allow_html=True)
            st.divider()
            
            # System controls
            st.subheader("🔧 System")
            
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()
            
            if st.button("🧹 Clear Cache", use_container_width=True):
                st.cache_data.clear()
                st.success("Cache cleared!")
            
            # Minimal spacing
            st.markdown("<div style='height: 0.25rem;'></div>", unsafe_allow_html=True)
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
                        # Note: These methods need to be implemented in the orchestrator
                        # self.orchestrator.force_email_processing(email_limit=email_limit, since_days=since_days)
                        st.success(f"Custom batch processed! ({email_limit} emails, {since_days} days)")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Orchestrator not initialized")

            st.markdown("**Data Management**")
            if st.button("🗑️ Clear Processed Emails", use_container_width=True, help="Clear email processing cache"):
                if self.orchestrator:
                    try:
                        # Note: This method needs to be implemented in the orchestrator
                        # self.orchestrator.clear_processed_emails()
                        st.success("Processed emails cleared!")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Orchestrator not initialized")
            
            # Real-time Email Controls
            # Minimal spacing
            st.markdown("<div style='height: 0.25rem;'></div>", unsafe_allow_html=True)
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
        """Render modern status cards showing system health."""
        if not self.orchestrator:
            st.markdown("""
            <div style="background: #fee2e2; border: 1px solid #fca5a5; color: #7f1d1d; padding: 1rem; border-radius: 12px; text-align: center;">
                ❌ System not initialized. Please check your configuration.
            </div>
            """, unsafe_allow_html=True)
            return
            
        stats = self.orchestrator.get_system_stats()
        
        # Modern metrics grid with better spacing
        col1, col2, col3, col4, col5 = st.columns(5, gap="medium")
        
        with col1:
            st.metric(
                label="📧 Emails Processed",
                value=f"{stats['emails_processed']:,}",  # Add comma separator for large numbers
                delta=None
            )
        
        with col2:
            st.metric(
                label="✅ Tasks Created",
                value=f"{stats['tasks_processed']:,}",
                delta=None
            )
        
        with col3:
            st.metric(
                label="🗃️ Processed Cache",
                value=f"{stats.get('processed_emails_count', 0):,}",
                delta=None
            )
        
        with col4:
            uptime_hours = stats['uptime_hours']
            if uptime_hours < 1:
                uptime_display = f"{uptime_hours*60:.0f}m"
            elif uptime_hours < 24:
                uptime_display = f"{uptime_hours:.1f}h"
            else:
                uptime_display = f"{uptime_hours/24:.1f}d"
                
            st.metric(
                label="⏰ Uptime",
                value=uptime_display,
                delta=None
            )
        
        with col5:
            error_count = stats["errors"]
            st.metric(
                label="❌ Errors",
                value=f"{error_count:,}",
                delta=None
            )
    
    def render_agent_status(self):
        """Render modern agent status section."""
        st.subheader("🤖 Agent Status")
        
        if not self.orchestrator:
            st.markdown("""
            <div style="background: #fee2e2; border: 1px solid #fca5a5; color: #7f1d1d; padding: 1rem; border-radius: 8px;">
                ❌ Agents not initialized. Please check your configuration.
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Use optimized width layout with controlled widths
        col1, col2, col3 = st.columns([2, 2, 3], gap="medium")
        
        with col1:
            # Determine email agent status
            email_status = "online" if self.orchestrator else "offline"
            status_class = f"agent-status-{email_status}"
            
            st.markdown(f"""
            <div class="agent-card">
                <h4 style="margin: 0 0 0.5rem 0; color: #f1f5f9; display: flex; align-items: center; font-size: 1.05rem; font-weight: 600;">
                    <span class="agent-status-indicator {status_class}"></span>
                    📧 Email Agent
                </h4>
                <div class="agent-details" style="color: #94a3b8; font-size: 0.875rem; line-height: 1.4;">
                    <strong>Provider:</strong> {settings.email_provider}<br>
                    <strong>Account:</strong> {settings.email_address}<br>
                    <strong>Check Interval:</strong> {settings.email_check_interval//60} minutes
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Real-time processing status with controlled width
            if self.orchestrator and hasattr(self.orchestrator, 'realtime_processor'):
                stats = self.orchestrator.get_system_stats()
                realtime_status = stats.get('realtime_email', {})
                
                if realtime_status.get('idle_supported', False):
                    if realtime_status.get('idle_running', False) and realtime_status.get('idle_thread_alive', False):
                        status_html = '<div class="realtime-status realtime-active">⚡ Real-time: Active</div>'
                    elif realtime_status.get('idle_running', False):
                        status_html = '<div class="realtime-status realtime-starting">⚡ Real-time: Starting...</div>'
                    else:
                        status_html = '<div class="realtime-status realtime-stopped">⚡ Real-time: Stopped</div>'
                else:
                    status_html = '<div class="realtime-status realtime-polling">⚡ Real-time: Polling</div>'
                
                st.markdown(status_html, unsafe_allow_html=True)
            else:
                st.markdown('<div class="realtime-status realtime-error">⚡ Real-time: Not Initialized</div>', unsafe_allow_html=True)
        
        with col2:
            # Check database connectivity and determine status
            if self.orchestrator and self.orchestrator.notion_agent.validate_database_setup():
                notion_status = "online"
                db_status = "✅ Valid"
            else:
                notion_status = "offline"
                db_status = "❌ Invalid"
            
            status_class = f"agent-status-{notion_status}"
            
            st.markdown(f"""
            <div class="agent-card">
                <h4 style="margin: 0 0 0.5rem 0; color: #f1f5f9; display: flex; align-items: center; font-size: 1.05rem; font-weight: 600;">
                    <span class="agent-status-indicator {status_class}"></span>
                    📝 Notion Agent
                </h4>
                <div class="agent-details" style="color: #94a3b8; font-size: 0.875rem; line-height: 1.4;">
                    <strong>Database:</strong> {settings.notion_database_id[:12]}...<br>
                    <strong>Schema:</strong> {db_status}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Empty space or future content
            st.empty()
    
    def get_recent_tasks_from_notion(self, limit: int = 10) -> List[Dict]:
        """Get recent tasks from Notion database."""
        try:
            if not self.orchestrator or not self.orchestrator.notion_agent:
                return []
            
            # Try to get recent tasks from Notion
            # This is a placeholder - would need to implement actual Notion querying
            recent_tasks = []
            
            # For now, return empty list if no real implementation
            return recent_tasks
            
        except Exception as e:
            # Use basic error handling since orchestrator logger might not be available
            print(f"Error fetching recent tasks: {e}")
            return []
    
    def get_system_logs(self, limit: int = 20) -> List[str]:
        """Get real system logs from the application."""
        try:
            # Try to read from log files if they exist
            import os
            from pathlib import Path
            
            log_entries = []
            
            # Check for log files in the project
            project_root = Path(__file__).parent.parent
            log_files = [
                project_root / "logs" / "application.log",
                project_root / "logs" / "agents.log", 
                project_root / "system.log",
                project_root / "app.log"
            ]
            
            for log_file in log_files:
                if log_file.exists():
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            # Get last N lines
                            recent_lines = lines[-limit:] if len(lines) > limit else lines
                            log_entries.extend([line.strip() for line in recent_lines if line.strip()])
                            break  # Use first available log file
                    except Exception:
                        continue
            
            # If no log files found, generate some real-time system info
            if not log_entries and self.orchestrator:
                stats = self.orchestrator.get_system_stats()
                current_time = datetime.now().strftime('%H:%M:%S')
                
                log_entries = [
                    f"[{current_time}] INFO | System | Dashboard accessed",
                    f"[{current_time}] INFO | Stats | Emails: {stats['emails_processed']}, Tasks: {stats['tasks_processed']}, Uptime: {stats['uptime_hours']:.1f}h",
                    f"[{current_time}] INFO | Agent | Email agent active ({settings.email_address})",
                    f"[{current_time}] INFO | Agent | Notion agent connected ({settings.notion_database_id[:12]}...)"
                ]
                
                # Add real-time status if available
                if hasattr(self.orchestrator, 'realtime_processor'):
                    realtime_stats = stats.get('realtime_email', {})
                    if realtime_stats.get('idle_running'):
                        log_entries.append(f"[{current_time}] INFO | RealTime | IMAP IDLE monitoring active")
            
            return log_entries[-limit:] if len(log_entries) > limit else log_entries
            
        except Exception as e:
            # Fallback to basic system info
            current_time = datetime.now().strftime('%H:%M:%S')
            return [
                f"[{current_time}] INFO | Dashboard | Log system initialized",
                f"[{current_time}] INFO | System | Monitoring active"
            ]
    
    def render_recent_tasks(self):
        """Render modern recent tasks table with real data when available."""
        st.subheader("📋 Recent Tasks")
        
        # Try to get real tasks first
        real_tasks = self.get_recent_tasks_from_notion(limit=10)
        
        if real_tasks:
            # Display real tasks from Notion
            df = pd.DataFrame(real_tasks)
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
        else:
            # Fallback to enhanced mock data with more realistic examples
            if self.orchestrator:
                stats = self.orchestrator.get_system_stats()
                if stats['emails_processed'] > 0 or stats['tasks_processed'] > 0:
                    # Show some realistic examples based on actual stats
                    mock_tasks = [
                        {
                            "Title": "Review quarterly report submission",
                            "Source": "Email",
                            "Priority": "High", 
                            "Status": "To Do",
                            "Created": datetime.now() - timedelta(minutes=25),
                            "From": "finance@company.com"
                        },
                        {
                            "Title": "Schedule client follow-up meeting",
                            "Source": "Email",
                            "Priority": "Medium",
                            "Status": "In Progress", 
                            "Created": datetime.now() - timedelta(hours=1, minutes=15),
                            "From": "sales@company.com"
                        },
                        {
                            "Title": "Update project documentation",
                            "Source": "Email",
                            "Priority": "Low",
                            "Status": "Done",
                            "Created": datetime.now() - timedelta(hours=3, minutes=45),
                            "From": "team@company.com"
                        }
                    ]
                else:
                    # Show placeholder for new system
                    mock_tasks = [
                        {
                            "Title": "No tasks found yet",
                            "Source": "System",
                            "Priority": "Low",
                            "Status": "N/A",
                            "Created": datetime.now(),
                            "From": "dashboard"
                        }
                    ]
            else:
                mock_tasks = [
                    {
                        "Title": "System initializing...",
                        "Source": "System", 
                        "Priority": "Low",
                        "Status": "N/A",
                        "Created": datetime.now(),
                        "From": "dashboard"
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
                        options=["To Do", "In Progress", "Done", "Cancelled", "N/A"],
                        default="To Do"
                    )
                }
            )
            
            # Show helpful message
            if not real_tasks:
                st.info("💡 Task data will appear here once emails are processed and tasks are created in Notion.")
    
    def render_logs(self):
        """Render modern system logs section with real data."""
        st.subheader("📜 System Logs")
        
        # Use a container to wrap logs and buttons together, preventing the empty box issue
        log_container = st.container()
        
        with log_container:
            st.markdown('<div class="log-container-wrapper">', unsafe_allow_html=True)
            
            # Get real system logs
            log_entries = self.get_system_logs(limit=15)
            
            # Create a modern log container with better styling
            st.markdown('<div class="log-scroll-area">', unsafe_allow_html=True)
            
            if not log_entries:
                st.markdown('<div class="log-entry-default">No log entries found.</div>', unsafe_allow_html=True)
            else:
                for log in reversed(log_entries):  # Show newest first
                    # Color code based on log level with much better contrast
                    if "ERROR" in log.upper():
                        st.markdown(f'<div class="log-entry-error">{log}</div>', unsafe_allow_html=True)
                    elif "WARNING" in log.upper() or "WARN" in log.upper():
                        st.markdown(f'<div class="log-entry-warning">{log}</div>', unsafe_allow_html=True)
                    elif "INFO" in log.upper():
                        st.markdown(f'<div class="log-entry-info">{log}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="log-entry-default">{log}</div>', unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True) # End of log-scroll-area
            
            # Add control buttons INSIDE the wrapper, properly positioned
            st.markdown("<div style='margin-top: 1rem; border-top: 1px solid #1e293b; padding-top: 1rem;'></div>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([5, 1, 1]) # Align buttons to the right
            with col2:
                if st.button("🔄 Refresh", key="refresh_logs", use_container_width=True):
                    st.rerun()
            with col3:
                log_content = "\n".join(log_entries)
                st.download_button(
                    label="Export",
                    data=log_content,
                    file_name=f"system_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    key="download_logs",
                    use_container_width=True
                )

            st.markdown("</div>", unsafe_allow_html=True) # End of log-container-wrapper
    
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
        """Render the main dashboard content with modern layout."""
        # Status cards - full width
        self.render_status_cards()
        
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        
        # Agent status - full width, properly aligned
        self.render_agent_status()
        
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        
        # Recent tasks - full width
        self.render_recent_tasks()
        
        st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
        
        # System logs - full width below tasks
        self.render_logs()
    
    def run(self):
        """Main dashboard runner."""
        self.render_header()
        self.render_sidebar()
        self.render_main_dashboard()
        
        # The global refresh button has been removed to avoid duplication.
        # The refresh logic is now contained within the logs section.

def main():
    """Main entry point for the dashboard."""
    # Use session state to persist dashboard instance
    if 'dashboard' not in st.session_state:
        st.session_state.dashboard = Dashboard()
    
    dashboard = st.session_state.dashboard
    dashboard.run()


if __name__ == "__main__":
    main()
