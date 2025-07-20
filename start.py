#!/usr/bin/env python3
"""
AI Agents Swarm - Full System Launcher
======================================

This script starts the complete AI Agents Swarm system including:
- FastAPI backend server
- Background email processing agents
- React dashboard frontend

Usage:
    python start.py                    # Starts complete system

Works on:
- Windows (with Node.js 18+ and Python 3.8+ installed)
- Linux (with Node.js 18+ and Python 3.8+ installed)  
- macOS (with Node.js 18+ and Python 3.8+ installed)

Requirements:
- Python 3.8+ with packages from requirements.txt
- Node.js 18+ and npm 8+
- React dashboard dependencies installed (npm install in dashboard-react/)

The script will:
1. Check Python and Node.js environments
2. Install dependencies if needed
3. Start FastAPI backend server
4. Start background processing agents
5. Start React development server
6. Open the dashboard in your browser
"""
import os
import sys
import subprocess
import platform
import webbrowser
import time
import logging
import signal
import atexit
from pathlib import Path
from typing import List, Tuple, Optional

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.resolve()

# Platform detection
IS_WINDOWS = platform.system() == "Windows"

def setup_logging():
    """Setup simple logging."""
    logger = logging.getLogger("system-launcher")
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', 
                                datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger

logger = setup_logging()

class SystemLauncher:
    """Complete system launcher for AI Agents Swarm."""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.react_dashboard_path = self.project_root / "dashboard-react"
        self.processes: List[Tuple[str, subprocess.Popen]] = []
        
        # Kill any existing processes on our ports before starting
        self.cleanup_existing_processes()
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
        
        # Set up signal handlers for proper cleanup
        if IS_WINDOWS:
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)  # Handle Ctrl+C
        else:
            signal.signal(signal.SIGTERM, self._signal_handler)
            signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"[STOP] Received signal {signum}, shutting down...")
        self.cleanup()
        sys.exit(0)
    
    def cleanup_existing_processes(self):
        """Safely check for and handle existing processes on ports 3000 and 8000."""
        logger.info("[CLEANUP] Checking for existing processes on ports 3000 and 8000...")
        
        ports_to_clean = [3000, 8000]
        
        for port in ports_to_clean:
            try:
                if IS_WINDOWS:
                    # Find processes using the port
                    result = subprocess.run(
                        f'netstat -ano | findstr :{port}',
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.stdout:
                        lines = result.stdout.strip().split('\n')
                        pids_to_check = set()
                        
                        for line in lines:
                            parts = line.split()
                            if len(parts) >= 5 and f':{port}' in parts[1]:
                                pid = parts[-1]
                                if pid.isdigit() and pid != '0':
                                    pids_to_check.add(pid)
                        
                        for pid in pids_to_check:
                            if self._is_safe_to_kill(pid, port):
                                try:
                                    logger.info(f"[CLEANUP] Killing our app process PID {pid} using port {port}")
                                    subprocess.run(
                                        f'taskkill /F /PID {pid}',
                                        shell=True,
                                        capture_output=True,
                                        check=False
                                    )
                                except Exception as e:
                                    logger.warning(f"[CLEANUP] Could not kill PID {pid}: {e}")
                            else:
                                self._handle_unknown_process(pid, port)
                else:
                    # Unix-like systems
                    result = subprocess.run(
                        f'lsof -ti:{port}',
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.stdout:
                        pids = result.stdout.strip().split('\n')
                        for pid in pids:
                            if pid.strip():
                                if self._is_safe_to_kill(pid, port):
                                    try:
                                        logger.info(f"[CLEANUP] Killing our app process PID {pid} using port {port}")
                                        subprocess.run(f'kill -9 {pid}', shell=True, check=False)
                                    except Exception as e:
                                        logger.warning(f"[CLEANUP] Could not kill PID {pid}: {e}")
                                else:
                                    self._handle_unknown_process(pid, port)
                                    
            except Exception as e:
                logger.warning(f"[CLEANUP] Error checking port {port}: {e}")
        
        # Give processes time to die
        time.sleep(1)
    
    def _is_safe_to_kill(self, pid, port):
        """Check if a process is safe to kill (belongs to our app)."""
        try:
            if IS_WINDOWS:
                # Get process name and command line
                result = subprocess.run(
                    f'wmic process where "ProcessId={pid}" get Name,CommandLine /format:csv',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines[1:]:  # Skip header
                        if line.strip():
                            parts = line.split(',', 2)
                            if len(parts) >= 3:
                                command_line = parts[2].lower()
                                process_name = parts[1].lower()
                                
                                # Check if it's clearly our app
                                our_app_indicators = [
                                    'dashboard-react',
                                    'npm start',
                                    'react-scripts',
                                    'next dev',
                                    'fastapi',
                                    'uvicorn',
                                    'agents',
                                    str(PROJECT_ROOT).lower(),
                                ]
                                
                                if any(indicator in command_line for indicator in our_app_indicators):
                                    logger.info(f"[SAFE] Process {pid} identified as our app: {process_name}")
                                    return True
            else:
                # Unix-like systems
                result = subprocess.run(
                    f'ps -p {pid} -o comm,args --no-headers',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if result.stdout:
                    process_info = result.stdout.strip().lower()
                    our_app_indicators = [
                        'dashboard-react',
                        'npm start',
                        'react-scripts',
                        'next dev',
                        'fastapi',
                        'uvicorn',
                        'agents',
                        str(PROJECT_ROOT).lower(),
                    ]
                    
                    if any(indicator in process_info for indicator in our_app_indicators):
                        logger.info(f"[SAFE] Process {pid} identified as our app")
                        return True
                        
        except Exception as e:
            logger.warning(f"[SAFE] Could not verify process {pid}: {e}")
        
        return False
    
    def _handle_unknown_process(self, pid, port):
        """Handle unknown processes that might not be ours."""
        try:
            # Get process details for user information
            if IS_WINDOWS:
                result = subprocess.run(
                    f'wmic process where "ProcessId={pid}" get Name,CommandLine /format:csv',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                process_info = "Unknown process"
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines[1:]:
                        if line.strip():
                            parts = line.split(',', 2)
                            if len(parts) >= 2:
                                process_info = f"{parts[1]} (PID: {pid})"
                                break
            else:
                result = subprocess.run(
                    f'ps -p {pid} -o comm --no-headers',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                process_info = f"{result.stdout.strip()} (PID: {pid})" if result.stdout else f"Unknown process (PID: {pid})"
            
            logger.warning(f"[WARNING] Port {port} is used by: {process_info}")
            logger.warning(f"[WARNING] This process is not recognized as part of our app.")
            
            response = input(f"Do you want to kill this process to free port {port}? (y/N): ").strip().lower()
            
            if response in ['y', 'yes']:
                try:
                    if IS_WINDOWS:
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True, check=False)
                    else:
                        subprocess.run(f'kill -9 {pid}', shell=True, check=False)
                    logger.info(f"[KILL] User authorized killing process {pid}")
                except Exception as e:
                    logger.error(f"[ERROR] Failed to kill process {pid}: {e}")
            else:
                logger.info(f"[SKIP] Process {pid} on port {port} left running (user choice)")
                logger.warning(f"[WARNING] Port {port} conflict may cause startup issues")
                
        except Exception as e:
            logger.error(f"[ERROR] Could not handle unknown process {pid}: {e}")
        
    def check_python_environment(self):
        """Check if Python environment is ready."""
        logger.info("[PYTHON] Checking Python environment...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            logger.error(f"[ERROR] Python 3.8+ required, found {python_version.major}.{python_version.minor}")
            return False
        
        logger.info(f"[OK] Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Check required Python packages
        required_packages = [
            'fastapi',
            'uvicorn',
            'loguru',
            'schedule',
            'requests'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"[OK] {package}")
            except ImportError:
                missing_packages.append(package)
                logger.error(f"[ERROR] {package}")
        
        if missing_packages:
            logger.error("Missing Python dependencies:")
            logger.error(f"pip install {' '.join(missing_packages)}")
            logger.error("Or install all dependencies with:")
            logger.error("pip install -r requirements.txt")
            return False
        
        return True
        
    def check_node_environment(self):
        """Check if Node.js and npm are available."""
        logger.info("[CHECK] Checking Node.js environment...")
        
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                node_version = result.stdout.strip()
                logger.info(f"[OK] Node.js: {node_version}")
            else:
                logger.error("[ERROR] Node.js not working properly")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.error("[ERROR] Node.js not found")
            logger.error("Please install Node.js 18+ from https://nodejs.org/")
            return False
        
        # Check npm (try both npm and npm.cmd on Windows)
        npm_commands = ['npm.cmd', 'npm'] if IS_WINDOWS else ['npm']
        npm_found = False
        
        for npm_cmd in npm_commands:
            try:
                result = subprocess.run([npm_cmd, '--version'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    npm_version = result.stdout.strip()
                    logger.info(f"[OK] npm: {npm_version} (using {npm_cmd})")
                    npm_found = True
                    break
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        if not npm_found:
            logger.error("[ERROR] npm not found")
            logger.error("Please ensure npm is installed and in your PATH.")
            logger.error("Try running 'npm --version' in your command prompt.")
            logger.error("If that fails, you may need to reinstall Node.js from https://nodejs.org/")
            return False
        
        return True
    
    def check_react_dashboard(self):
        """Check if React dashboard is properly set up."""
        logger.info("[FOLDER] Checking React dashboard...")
        
        if not self.react_dashboard_path.exists():
            logger.error("[ERROR] React dashboard directory not found")
            logger.error("Please ensure dashboard-react/ directory exists")
            return False
        
        package_json_path = self.react_dashboard_path / "package.json"
        if not package_json_path.exists():
            logger.error("[ERROR] React dashboard package.json not found")
            return False
        
        logger.info("[OK] React dashboard directory found")
        return True
    
    def install_react_dependencies(self):
        """Install React dashboard dependencies if needed."""
        node_modules_path = self.react_dashboard_path / "node_modules"
        
        if node_modules_path.exists():
            logger.info("[OK] React dependencies already installed")
            return True
        
        logger.info("[INSTALL] Installing React dashboard dependencies...")
        logger.info("This may take a few minutes...")
        
        # Try different npm commands for Windows compatibility
        npm_commands = ['npm.cmd', 'npm'] if IS_WINDOWS else ['npm']
        
        for npm_cmd in npm_commands:
            try:
                process = subprocess.run(
                    [npm_cmd, "install"],
                    cwd=self.react_dashboard_path,
                    check=True,
                    capture_output=True,
                    text=True
                )
                
                logger.info("[OK] React dependencies installed successfully")
                return True
                
            except FileNotFoundError:
                continue  # Try next npm command
            except subprocess.CalledProcessError as e:
                logger.error(f"[ERROR] Failed to install dependencies using {npm_cmd}")
                logger.error(f"Error: {e}")
                if e.stdout:
                    logger.error(f"stdout: {e.stdout}")
                if e.stderr:
                    logger.error(f"stderr: {e.stderr}")
                return False
            except Exception as e:
                logger.error(f"[ERROR] Unexpected error during installation with {npm_cmd}: {e}")
                continue
        
        logger.error("[ERROR] Could not find a working npm command")
        logger.error("Please ensure npm is properly installed and in your PATH")
        return False

    def get_process_creation_flags(self):
        """Get appropriate process creation flags for the platform."""
        if IS_WINDOWS:
            # Use CREATE_NEW_PROCESS_GROUP but handle signals properly
            return subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_BREAKAWAY_FROM_JOB
        else:
            return 0

    def start_api_server(self):
        """Start the FastAPI backend server."""
        logger.info("[START] Starting API server...")
        
        cmd = [
            sys.executable,
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
            
            # Create process with proper cleanup handling
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                env=env,
                creationflags=self.get_process_creation_flags() if IS_WINDOWS else 0
            )
            
            self.processes.append(("API Server", process))
            logger.info(f"[OK] API server started (PID: {process.pid})")
            return process
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to start API server: {e}")
            return None

    def start_background_processing(self):
        """Start the background email processing agents."""
        logger.info("[AI] Starting background agents...")
        
        cmd = [
            sys.executable,
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
                creationflags=self.get_process_creation_flags() if IS_WINDOWS else 0
            )
            
            self.processes.append(("Background Agents", process))
            logger.info(f"[OK] Background agents started (PID: {process.pid})")
            return process
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to start background agents: {e}")
            return None
    
    def start_react_dashboard(self):
        """Start the React dashboard frontend."""
        logger.info("[WEB] Starting React dashboard...")
        
        # Try different npm commands for Windows compatibility
        npm_commands = ['npm.cmd', 'npm'] if IS_WINDOWS else ['npm']
        
        for npm_cmd in npm_commands:
            try:
                # Set environment variables
                env = os.environ.copy()
                env['API_BASE_URL'] = 'http://localhost:8000'
                
                # Start the development server
                process = subprocess.Popen(
                    [npm_cmd, "run", "dev"],
                    cwd=self.react_dashboard_path,
                    env=env,
                    creationflags=self.get_process_creation_flags() if IS_WINDOWS else 0
                )
                
                self.processes.append(("React Dashboard", process))
                logger.info(f"[OK] React dashboard started (PID: {process.pid}) using {npm_cmd}")
                return process
                
            except FileNotFoundError:
                continue  # Try next npm command
            except Exception as e:
                logger.error(f"[ERROR] Failed to start React dashboard using {npm_cmd}: {e}")
                continue
        
        logger.error("[ERROR] Could not find a working npm command to start the dashboard")
        return None

    def wait_for_service(self, url: str, name: str, timeout: int = 30) -> bool:
        """Wait for a service to be ready."""
        logger.info(f"[WAIT] Waiting for {name} to be ready...")
        
        try:
            import requests
            
            for i in range(timeout):
                try:
                    response = requests.get(url, timeout=2)
                    if response.status_code == 200:
                        logger.info(f"[OK] {name} is ready at {url}")
                        return True
                except:
                    pass
                time.sleep(1)
                
            logger.warning(f"[WARN]  {name} may not be ready yet")
            return False
            
        except ImportError:
            logger.warning("Requests not available, skipping service checks")
            time.sleep(5)  # Just wait a bit
            return True

    def open_browser(self):
        """Open the dashboard in the browser."""
        dashboard_url = "http://localhost:3000"
        
        try:
            logger.info(f"[WEB] Opening dashboard in browser: {dashboard_url}")
            webbrowser.open(dashboard_url)
            return True
        except Exception as e:
            logger.warning(f"Could not open browser: {e}")
            logger.info(f"Please open {dashboard_url} manually")
            return False

    def cleanup(self):
        """Clean up all processes."""
        if not self.processes:
            return
            
        logger.info("[STOP] Shutting down all processes...")
        
        for name, process in self.processes:
            try:
                if process.poll() is None:
                    logger.info(f"Terminating {name} (PID: {process.pid})...")
                    
                    if IS_WINDOWS:
                        # On Windows, try to terminate gracefully first
                        try:
                            process.terminate()
                            process.wait(timeout=5)
                            logger.info(f"[OK] {name} terminated gracefully")
                        except subprocess.TimeoutExpired:
                            # Force kill if graceful termination fails
                            logger.warning(f"Force killing {name}...")
                            subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)], 
                                         shell=True, capture_output=True)
                            logger.info(f"[KILL] {name} force killed")
                    else:
                        # On Unix-like systems
                        process.send_signal(signal.SIGTERM)
                        try:
                            process.wait(timeout=5)
                            logger.info(f"[OK] {name} terminated gracefully")
                        except subprocess.TimeoutExpired:
                            logger.warning(f"Force killing {name}...")
                            process.kill()
                            process.wait()
                            logger.info(f"[KILL] {name} force killed")
                else:
                    logger.info(f"[OK] {name} already stopped")
                        
            except Exception as e:
                logger.error(f"Error terminating {name}: {e}")
                # Try force kill as last resort
                if IS_WINDOWS:
                    try:
                        subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)], 
                                     shell=True, capture_output=True)
                    except:
                        pass
        
        self.processes.clear()
        logger.info("All processes terminated")
    
    def run(self):
        """Run the complete AI Agents Swarm system."""
        try:
            logger.info("AI Agents Swarm - Full System Startup")
            logger.info("=" * 50)
            
            # Check environments
            if not self.check_python_environment():
                logger.error("[ERROR] Python environment check failed")
                return False
            
            if not self.check_node_environment():
                logger.error("[ERROR] Node.js environment check failed")
                return False
            
            if not self.check_react_dashboard():
                logger.error("[ERROR] React dashboard check failed")
                return False
            
            # Install dependencies
            if not self.install_react_dependencies():
                logger.error("[ERROR] React dependency installation failed")
                return False
            
            logger.info("")
            logger.info("[START] Starting all system components...")
            
            # Start API server
            api_process = self.start_api_server()
            if api_process:
                time.sleep(3)  # Give API server time to start
            else:
                logger.error("[ERROR] Failed to start API server")
                return False
            
            # Start background processing
            bg_process = self.start_background_processing()
            if bg_process:
                time.sleep(3)  # Give background processing time to start
            else:
                logger.warning("[WARN]  Background agents failed to start (may be configuration issue)")
            
            # Start React dashboard
            dashboard_process = self.start_react_dashboard()
            if dashboard_process:
                time.sleep(5)  # Give dashboard time to start
            else:
                logger.error("[ERROR] Failed to start React dashboard")
                return False
            
            # Wait for services to be ready
            logger.info("")
            logger.info("[CHECK] Checking service health...")
            self.wait_for_service("http://localhost:8000/health", "API Server")
            self.wait_for_service("http://localhost:3000", "React Dashboard", timeout=15)
            
            # Open browser
            time.sleep(2)
            self.open_browser()
            
            logger.info("")
            logger.info("[SUCCESS] AI Agents Swarm is now running!")
            logger.info("[INFO] Service URLs:")
            logger.info("   [WEB] Dashboard: http://localhost:3000")
            logger.info("   [API] API Server: http://localhost:8000")
            logger.info("   [STATS] Health Check: http://localhost:8000/health")
            logger.info("   [DOCS] API Docs: http://localhost:8000/docs")
            logger.info("")
            logger.info("[INFO] The dashboard should now show real data from the running agents!")
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
                        logger.error(f"[DEAD] {name} has stopped unexpectedly")
                    
                    if "API Server" in dead_processes or "React Dashboard" in dead_processes:
                        logger.error("Critical processes died. Shutting down...")
                        return False
                        
        except KeyboardInterrupt:
            logger.info("[STOP] Received shutdown signal")
            return True
        except Exception as e:
            logger.error(f"[CRASH] System error: {e}")
            return False
        finally:
            self.cleanup()
            
        return True


def main():
    """Main entry point."""
    launcher = SystemLauncher()
    
    try:
        success = launcher.run()
        
        if success:
            logger.info("[BYE] Goodbye!")
            return 0
        else:
            logger.error("[ERROR] System failed to start properly")
            return 1
    except KeyboardInterrupt:
        logger.info("[STOP] Interrupted by user")
        launcher.cleanup()
        return 0
    except Exception as e:
        logger.error(f"[CRASH] Unexpected error: {e}")
        launcher.cleanup()
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n[STOP] System interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
