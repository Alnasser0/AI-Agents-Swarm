#!/usr/bin/env python3
"""
AI Agents Swarm - Universal Startup Script
==========================================

This script starts all components of the AI Agents Swarm system:
- API Server (FastAPI)
- Streamlit Dashboard  
- Background email processing
- Real-time email monitoring

Usage:
    python start.py

Works on:
- Windows (any Python environment: conda, venv, global, pyenv)
- Linux (any Python environment: conda, venv, global, pyenv)
- macOS (any Python environment: conda, venv, global, pyenv)

Requirements:
- Python 3.8+
- All dependencies from requirements.txt installed

Environment Detection:
- Automatically uses the current Python interpreter
- Works with conda environments, virtual environments, and global Python
- Cross-platform compatible
"""

import os
import sys
import time
import subprocess
import signal
import webbrowser
import platform
from pathlib import Path

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_MACOS = platform.system() == "Darwin"

# Environment detection
def detect_environment():
    """Detect the current Python environment."""
    env_info = {
        'python_executable': sys.executable,
        'python_version': sys.version.split()[0],
        'environment_type': 'unknown',
        'environment_name': None,
        'platform': platform.system(),
        'architecture': platform.machine()
    }
    
    # Detect conda environment
    if 'CONDA_DEFAULT_ENV' in os.environ:
        env_info['environment_type'] = 'conda'
        env_info['environment_name'] = os.environ['CONDA_DEFAULT_ENV']
    elif 'CONDA_PREFIX' in os.environ:
        env_info['environment_type'] = 'conda'
        env_info['environment_name'] = Path(os.environ['CONDA_PREFIX']).name
    # Detect virtual environment
    elif hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        env_info['environment_type'] = 'venv'
        if 'VIRTUAL_ENV' in os.environ:
            env_info['environment_name'] = Path(os.environ['VIRTUAL_ENV']).name
        else:
            env_info['environment_name'] = Path(sys.prefix).name
    # Detect pyenv
    elif 'PYENV_VERSION' in os.environ:
        env_info['environment_type'] = 'pyenv'
        env_info['environment_name'] = os.environ['PYENV_VERSION']
    else:
        env_info['environment_type'] = 'global'
        env_info['environment_name'] = 'system'
    
    return env_info


def setup_logging():
    """Setup simple logging without external dependencies."""
    import logging
    
    # Create simple logger
    logger = logging.getLogger("startup")
    logger.setLevel(logging.INFO)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', 
                                datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger


# Initialize logger
logger = setup_logging()


class SystemLauncher:
    """Universal system launcher that works across platforms and environments."""
    
    def __init__(self):
        self.processes = []
        self.project_root = PROJECT_ROOT
        self.env_info = detect_environment()
        self.python_executable = self.env_info['python_executable']
        
        self.print_environment_info()
        
    def print_environment_info(self):
        """Print detailed environment information."""
        logger.info(f"Platform: {self.env_info['platform']} {platform.release()} ({self.env_info['architecture']})")
        logger.info(f"Python: {self.env_info['python_version']}")
        logger.info(f"Environment: {self.env_info['environment_type'].upper()} ({self.env_info['environment_name']})")
        logger.info(f"Python executable: {self.python_executable}")
        logger.info(f"Working directory: {self.project_root}")
        
        # Additional conda info
        if self.env_info['environment_type'] == 'conda':
            if 'CONDA_PREFIX' in os.environ:
                logger.info(f"Conda prefix: {os.environ['CONDA_PREFIX']}")
        
        # Additional venv info
        elif self.env_info['environment_type'] == 'venv':
            if 'VIRTUAL_ENV' in os.environ:
                logger.info(f"Virtual env: {os.environ['VIRTUAL_ENV']}")
        
        logger.info("")
        
    def check_dependencies(self):
        """Check if required dependencies are installed."""
        logger.info("Checking dependencies...")
        
        required_modules = [
            'fastapi',
            'uvicorn', 
            'streamlit',
            'loguru',
            'schedule',
            'requests'
        ]
        
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
                logger.info(f"✅ {module}")
            except ImportError:
                missing_modules.append(module)
                logger.error(f"❌ {module}")
        
        if missing_modules:
            logger.error("Missing dependencies. Install them with:")
            logger.error(f"pip install {' '.join(missing_modules)}")
            logger.error("Or install all dependencies with:")
            logger.error("pip install -r requirements.txt")
            return False
            
        logger.info("All dependencies are installed!")
        return True
        
    def get_process_creation_flags(self):
        """Get appropriate process creation flags for the platform."""
        if IS_WINDOWS:
            return subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            return 0
    
    def get_python_command(self):
        """Get the appropriate Python command for the current environment."""
        # Always use the current Python executable to ensure consistency
        return [self.python_executable]
            
    def start_api_server(self):
        """Start the FastAPI server."""
        logger.info("Starting API server...")
        
        cmd = self.get_python_command() + [
            "-m", "uvicorn",
            "api.server:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ]
        
        try:
            # Set environment variables to ensure proper module resolution
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.project_root)
            
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=self.get_process_creation_flags()
            )
            
            self.processes.append(("API Server", process))
            logger.info(f"API server started (PID: {process.pid})")
            return process
            
        except Exception as e:
            logger.error(f"Failed to start API server: {e}")
            return None
    
    def start_background_processing(self):
        """Start the background email processing."""
        logger.info("Starting background email processing...")
        
        cmd = self.get_python_command() + [
            "-m", "agents.main"
        ]
        
        try:
            # Set environment variables to ensure proper module resolution
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.project_root)
            
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=self.get_process_creation_flags()
            )
            
            self.processes.append(("Background Processing", process))
            logger.info(f"Background processing started (PID: {process.pid})")
            return process
            
        except Exception as e:
            logger.error(f"Failed to start background processing: {e}")
            return None
    
    def start_dashboard(self):
        """Start the Streamlit dashboard."""
        logger.info("Starting Streamlit dashboard...")
        
        cmd = self.get_python_command() + [
            "-m", "streamlit", "run",
            "ui/dashboard.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ]
        
        try:
            # Set environment variables to ensure proper module resolution
            env = os.environ.copy()
            env['PYTHONPATH'] = str(self.project_root)
            
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=self.get_process_creation_flags()
            )
            
            self.processes.append(("Dashboard", process))
            logger.info(f"Dashboard started (PID: {process.pid})")
            return process
            
        except Exception as e:
            logger.error(f"Failed to start dashboard: {e}")
            return None
    
    def wait_for_service(self, url, name, timeout=30):
        """Wait for a service to be ready."""
        logger.info(f"Waiting for {name} to be ready...")
        
        try:
            import requests
            
            for i in range(timeout):
                try:
                    response = requests.get(url, timeout=2)
                    if response.status_code == 200:
                        logger.info(f"✅ {name} is ready at {url}")
                        return True
                except:
                    pass
                time.sleep(1)
                
            logger.warning(f"⚠️  {name} may not be ready yet")
            return False
            
        except ImportError:
            logger.warning("Requests not available, skipping service checks")
            time.sleep(5)  # Just wait a bit
            return True
    
    def open_browser(self):
        """Open the dashboard in the browser."""
        dashboard_url = "http://localhost:8501"
        
        try:
            logger.info(f"Opening dashboard in browser: {dashboard_url}")
            webbrowser.open(dashboard_url)
            return True
        except Exception as e:
            logger.warning(f"Could not open browser: {e}")
            logger.info(f"Please open {dashboard_url} manually")
            return False
    
    def cleanup(self):
        """Clean up all processes."""
        logger.info("Shutting down all processes...")
        
        for name, process in self.processes:
            try:
                if process.poll() is None:
                    logger.info(f"Terminating {name}")
                    
                    if IS_WINDOWS:
                        process.terminate()
                    else:
                        process.send_signal(signal.SIGTERM)
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=10)
                        logger.info(f"✅ {name} terminated gracefully")
                    except subprocess.TimeoutExpired:
                        logger.warning(f"Force killing {name}")
                        process.kill()
                        process.wait()
                        logger.info(f"🔴 {name} force killed")
                        
            except Exception as e:
                logger.error(f"Error terminating {name}: {e}")
        
        logger.info("All processes terminated")
    
    def run(self):
        """Run the complete system."""
        try:
            logger.info("🤖 AI Agents Swarm - System Startup")
            logger.info("=" * 50)
            
            # Show environment info
            logger.info("🔍 Environment Information:")
            logger.info(f"   Platform: {self.env_info['platform']} ({self.env_info['architecture']})")
            logger.info(f"   Python: {self.env_info['python_version']}")
            logger.info(f"   Environment: {self.env_info['environment_type'].upper()} - {self.env_info['environment_name']}")
            logger.info(f"   Executable: {self.python_executable}")
            logger.info("")
            
            # Check dependencies first
            if not self.check_dependencies():
                logger.error("❌ Dependency check failed. Please install missing packages.")
                return False
            
            logger.info("🚀 Starting all components...")
            
            # Start API server
            api_process = self.start_api_server()
            if api_process:
                time.sleep(3)  # Give API server time to start
            
            # Start background processing
            bg_process = self.start_background_processing()
            if bg_process:
                time.sleep(3)  # Give background processing time to start
            
            # Start dashboard
            dashboard_process = self.start_dashboard()
            if dashboard_process:
                time.sleep(3)  # Give dashboard time to start
            
            # Wait for services to be ready
            logger.info("⏳ Checking service health...")
            self.wait_for_service("http://localhost:8000/health", "API Server")
            self.wait_for_service("http://localhost:8501", "Dashboard")
            
            # Open browser
            time.sleep(2)
            self.open_browser()
            
            logger.info("🎉 System startup complete!")
            logger.info("📍 Service URLs:")
            logger.info("   - API Server: http://localhost:8000")
            logger.info("   - Dashboard: http://localhost:8501")
            logger.info("   - Health Check: http://localhost:8000/health")
            logger.info("")
            logger.info("Press Ctrl+C to stop all services...")
            
            # Keep the launcher running and monitor processes
            while True:
                time.sleep(5)  # Check every 5 seconds
                
                # Check if any critical process has died
                dead_processes = []
                for name, process in self.processes:
                    if process.poll() is not None:
                        dead_processes.append(name)
                
                if dead_processes:
                    for name in dead_processes:
                        logger.error(f"💀 {name} has stopped unexpectedly")
                    
                    logger.error("Critical processes died. Shutting down...")
                    return False
                        
        except KeyboardInterrupt:
            logger.info("🛑 Received shutdown signal")
            return True
        except Exception as e:
            logger.error(f"💥 System error: {e}")
            return False
        finally:
            self.cleanup()
            
        return True


def main():
    """Main entry point."""
    launcher = SystemLauncher()
    success = launcher.run()
    
    if success:
        logger.info("👋 Goodbye!")
        return 0
    else:
        logger.error("❌ System failed to start properly")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
