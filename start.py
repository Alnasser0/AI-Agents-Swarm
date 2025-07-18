#!/usr/bin/env python3
"""
AI Agents Swarm - Single Command Startup
=========================================

This script starts all components of the AI Agents Swarm system:
- API Server (FastAPI)
- Streamlit Dashboard
- Background email processing
- Real-time email monitoring

Usage:
    python start.py

The script will:
1. Start the API server in the background
2. Start the background email processing
3. Launch the Streamlit dashboard
4. Open the dashboard in your browser
"""

import os
import sys
import time
import subprocess
import signal
import webbrowser
from pathlib import Path
from loguru import logger

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss} | {level} | {message}")


class SystemLauncher:
    """Manages the startup of all system components."""
    
    def __init__(self):
        self.processes = []
        self.project_root = project_root
        self.check_conda_environment()
        
    def check_conda_environment(self):
        """Check if conda and the AI environment are available."""
        try:
            # Check if conda is available
            subprocess.run(["conda", "--version"], capture_output=True, check=True)
            
            # Check if AI environment exists
            result = subprocess.run(
                ["conda", "info", "--envs"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            if " ai " not in result.stdout and " ai*" not in result.stdout:
                logger.error("AI conda environment not found")
                logger.info("Please create it: conda create -n ai python=3.10")
                logger.info("Then install dependencies: conda activate ai && pip install -r requirements.txt")
                sys.exit(1)
                
            logger.info("AI conda environment verified")
            
        except subprocess.CalledProcessError:
            logger.error("Failed to check conda environments")
            sys.exit(1)
        except FileNotFoundError:
            logger.error("Conda not found. Please install Anaconda/Miniconda")
            sys.exit(1)
        
    def start_api_server(self):
        """Start the FastAPI server."""
        logger.info("Starting API server...")
        
        cmd = [
            "conda", "run", "--live-stream", "--name", "ai",
            "python", "-m", "uvicorn",
            "api.server:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ]
        
        process = subprocess.Popen(
            cmd,
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        
        self.processes.append(("API Server", process))
        logger.info("API server started (PID: {})", process.pid)
        return process
    
    def start_background_processing(self):
        """Start the background email processing."""
        logger.info("Starting background email processing...")
        
        cmd = [
            "conda", "run", "--live-stream", "--name", "ai",
            "python", "-m", "agents.main"
        ]
        
        process = subprocess.Popen(
            cmd,
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        
        self.processes.append(("Background Processing", process))
        logger.info("Background processing started (PID: {})", process.pid)
        return process
    
    def start_dashboard(self):
        """Start the Streamlit dashboard."""
        logger.info("Starting Streamlit dashboard...")
        
        cmd = [
            "conda", "run", "--live-stream", "--name", "ai",
            "python", "-m", "streamlit", "run",
            "ui/dashboard.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ]
        
        process = subprocess.Popen(
            cmd,
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        
        self.processes.append(("Dashboard", process))
        logger.info("Dashboard started (PID: {})", process.pid)
        return process
    
    def wait_for_services(self):
        """Wait for services to be ready."""
        logger.info("Waiting for services to start...")
        
        # Wait for API server
        import requests
        for i in range(30):
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    logger.info("API server is ready")
                    break
            except:
                time.sleep(1)
        
        # Wait for dashboard
        for i in range(30):
            try:
                response = requests.get("http://localhost:8501", timeout=2)
                if response.status_code == 200:
                    logger.info("Dashboard is ready")
                    break
            except:
                time.sleep(1)
    
    def open_browser(self):
        """Open the dashboard in the browser."""
        dashboard_url = "http://localhost:8501"
        logger.info("Opening dashboard in browser: {}", dashboard_url)
        
        try:
            webbrowser.open(dashboard_url)
        except Exception as e:
            logger.warning("Could not open browser: {}", e)
            logger.info("Please open {} manually", dashboard_url)
    
    def cleanup(self):
        """Clean up all processes."""
        logger.info("Shutting down all processes...")
        
        for name, process in self.processes:
            try:
                if process.poll() is None:
                    logger.info("Terminating {}", name)
                    if os.name == 'nt':
                        process.terminate()
                    else:
                        process.send_signal(signal.SIGTERM)
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        logger.warning("Force killing {}", name)
                        process.kill()
                        
            except Exception as e:
                logger.error("Error terminating {}: {}", name, e)
        
        logger.info("All processes terminated")
    
    def run(self):
        """Run the complete system."""
        try:
            logger.info("=== AI Agents Swarm System Startup ===")
            
            # Start all components
            self.start_api_server()
            time.sleep(2)  # Let API server start
            
            self.start_background_processing()
            time.sleep(2)  # Let background processing start
            
            self.start_dashboard()
            time.sleep(3)  # Let dashboard start
            
            # Wait for services to be ready
            self.wait_for_services()
            
            # Open browser
            self.open_browser()
            
            logger.info("=== System startup complete ===")
            logger.info("API Server: http://localhost:8000")
            logger.info("Dashboard: http://localhost:8501")
            logger.info("Press Ctrl+C to stop all services")
            
            # Keep the launcher running
            while True:
                time.sleep(1)
                
                # Check if any process has died
                for name, process in self.processes:
                    if process.poll() is not None:
                        logger.error("{} has stopped unexpectedly", name)
                        return
                        
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error("System error: {}", e)
        finally:
            self.cleanup()


def main():
    """Main entry point."""
    launcher = SystemLauncher()
    launcher.run()


if __name__ == "__main__":
    main()
