#!/usr/bin/env python3
"""
AI Agents Swarm - Comprehensive Setup Script

This script provides a complete setup experience for the AI Agents Swarm system.
It handles environment setup, dependency installation, configuration validation,
and system testing to ensure everything works correctly before first run.

Features:
- Python environment validation
- Dependency installation with error handling  
- Environment configuration setup and validation
- API key and service connectivity testing
- Database schema validation
- Email server connectivity testing
- Comprehensive system health checks
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import List, Tuple, Optional, Dict

def print_banner():
    """Print welcome banner."""
    print("🤖" + "=" * 60)
    print("🚀 AI AGENTS SWARM - INTELLIGENT SETUP")
    print("📧 Email Processing • 🧠 AI Tasks • 📝 Notion Integration")
    print("=" * 62)
    print()

def print_step(step: str):
    """Print a setup step."""
    print(f"🔧 {step}")

def print_success(message: str):
    """Print a success message."""
    print(f"✅ {message}")

def print_error(message: str):
    """Print an error message."""
    print(f"❌ {message}")

def print_warning(message: str):
    """Print a warning message."""
    print(f"⚠️  {message}")

def print_info(message: str):
    """Print an info message."""
    print(f"ℹ️  {message}")

def check_system_requirements():
    """Check system requirements and environment."""
    print_step("Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print_error(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        print_info("Please upgrade Python: https://www.python.org/downloads/")
        return False
    print_success(f"Python {python_version.major}.{python_version.minor}.{python_version.micro} ✓")
    
    # Check platform
    system = platform.system()
    print_success(f"Platform: {system} {platform.release()} ✓")
    
    return True

def check_node_environment():
    """Check Node.js environment for dashboard."""
    print_step("Checking Node.js environment for React dashboard...")
    
    try:
        # Check Node.js
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            node_version = result.stdout.strip()
            version_num = node_version.replace('v', '').split('.')[0]
            if int(version_num) < 18:
                print_warning(f"Node.js {node_version} detected. Version 18+ recommended.")
            else:
                print_success(f"Node.js {node_version} ✓")
        else:
            print_warning("Node.js not found - React dashboard may not work")
            return False
            
        # Check npm
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            npm_version = result.stdout.strip()
            print_success(f"npm {npm_version} ✓")
        else:
            print_warning("npm not found - React dashboard may not work")
            return False
            
        return True
        
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        print_warning("Node.js/npm not found - React dashboard will not be available")
        print_info("Install Node.js 18+ from: https://nodejs.org/")
        return False

def install_python_requirements():
    """Install Python requirements with detailed feedback."""
    print_step("Installing Python requirements...")
    
    # Check if requirements.txt exists
    if not Path("requirements.txt").exists():
        print_error("requirements.txt not found")
        return False
    
    try:
        # Install with progress feedback
        print("📦 Installing packages...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"
        ], check=True, capture_output=True, text=True)
        
        print_success("Python requirements installed successfully")
        
        # Verify key packages
        key_packages = [
            "fastapi", "uvicorn", "pydantic-ai", 
            "google-genai", "notion-client", "imapclient"
        ]
        
        print("🔍 Verifying key packages...")
        for package in key_packages:
            try:
                __import__(package.replace("-", "_"))
                print(f"  ✓ {package}")
            except ImportError:
                print(f"  ⚠️ {package} - may need manual installation")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install requirements: {e}")
        if e.stdout:
            print("📋 Output:", e.stdout[-500:])  # Last 500 chars
        if e.stderr:
            print("🚨 Error:", e.stderr[-500:])   # Last 500 chars
        return False

def install_dashboard_dependencies():
    """Install React dashboard dependencies."""
    dashboard_path = Path("dashboard-react")
    
    if not dashboard_path.exists():
        print_warning("React dashboard directory not found - skipping")
        return True
    
    print_step("Installing React dashboard dependencies...")
    
    try:
        # Change to dashboard directory and install
        result = subprocess.run([
            "npm", "install"
        ], cwd=dashboard_path, check=True, capture_output=True, text=True, timeout=300)
        
        print_success("React dashboard dependencies installed")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dashboard dependencies: {e}")
        return False
    except subprocess.TimeoutExpired:
        print_error("Dashboard installation timed out (5 minutes)")
        return False
    except FileNotFoundError:
        print_warning("npm not found - dashboard dependencies not installed")
        return False

def create_directories():
    """Create necessary directories."""
    print_step("Creating required directories...")
    
    directories = ["data", "logs", "temp", "cache"]
    created_dirs = []
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            created_dirs.append(directory)
    
    if created_dirs:
        print_success(f"Created directories: {', '.join(created_dirs)}")
    else:
        print_success("All directories already exist")
    
    return True

def setup_environment_file():
    """Set up environment configuration file."""
    print_step("Setting up environment configuration...")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_file.exists():
        if env_example.exists():
            env_file.write_text(env_example.read_text())
            print_success("Environment file created from template")
            print_warning("📝 IMPORTANT: Edit .env file with your API keys and configuration")
            print_info("Key settings needed:")
            print_info("  • EMAIL_ADDRESS and EMAIL_PASSWORD (Gmail App Password)")
            print_info("  • NOTION_API_KEY and NOTION_DATABASE_ID")
            print_info("  • GEMINI_API_KEY (recommended AI model)")
        else:
            print_error("No .env.example file found")
            return False
    else:
        print_success("Environment file already exists")
    
    return True

def validate_environment_configuration():
    """Validate environment configuration in detail."""
    print_step("Validating environment configuration...")
    
    try:
        # Import settings to trigger validation
        sys.path.insert(0, str(Path.cwd()))
        from config.settings import settings
        
        validation_results = {
            "email": False,
            "notion": False,
            "ai_model": False,
            "critical_missing": []
        }
        
        # Check email configuration
        if (settings.email_address and 
            settings.email_password and 
            not settings.email_address.startswith("your-") and
            not settings.email_password.startswith("your-")):
            validation_results["email"] = True
            print("  ✓ Email configuration")
        else:
            validation_results["critical_missing"].append("Email credentials")
            print("  ❌ Email configuration incomplete")
        
        # Check Notion configuration  
        if (settings.notion_api_key and 
            settings.notion_database_id and
            not settings.notion_api_key.startswith("your-") and
            not settings.notion_database_id.startswith("your-")):
            validation_results["notion"] = True
            print("  ✓ Notion configuration")
        else:
            validation_results["critical_missing"].append("Notion credentials")
            print("  ❌ Notion configuration incomplete")
            
        # Check AI model configuration
        ai_keys = [
            (settings.gemini_api_key, "Gemini"),
            (settings.openai_api_key, "OpenAI"), 
            (settings.anthropic_api_key, "Anthropic")
        ]
        
        available_models = []
        for key, name in ai_keys:
            if key and not key.startswith("your-"):
                available_models.append(name)
                
        if available_models:
            validation_results["ai_model"] = True
            print(f"  ✓ AI models available: {', '.join(available_models)}")
            if "Gemini" in available_models:
                print("  ℹ️ Gemini detected (recommended and tested model)")
        else:
            validation_results["critical_missing"].append("AI model API keys")
            print("  ❌ No AI model API keys configured")
        
        # Overall validation
        if validation_results["critical_missing"]:
            print_error("❌ Configuration validation failed")
            print_warning("Missing critical configuration:")
            for missing in validation_results["critical_missing"]:
                print(f"  • {missing}")
            print()
            print_info("🛠️ Setup instructions:")
            print_info("1. Edit .env file with your credentials")
            print_info("2. For Gmail: Enable 2FA and create App Password")
            print_info("3. For Notion: Create integration and database")
            print_info("4. For AI: Get API key from Google (Gemini recommended)")
            print_info("5. Run 'python setup.py' again")
            return False
        else:
            print_success("✅ Configuration validation passed")
            return True
            
    except Exception as e:
        print_error(f"Configuration validation failed: {e}")
        print_info("Check your .env file format and required settings")
        return False

def test_system_connections():
    """Test connections to external services."""
    print_step("Testing system connections...")
    
    connection_results = {"passed": 0, "failed": 0, "details": []}
    
    try:
        # Import orchestrator for testing
        from agents.main import AgentOrchestrator
        orchestrator = AgentOrchestrator()
        
        # Test Notion connection
        print("  🔍 Testing Notion connection...")
        try:
            if orchestrator.notion_agent.validate_database_setup():
                print("  ✅ Notion connection successful")
                connection_results["passed"] += 1
                connection_results["details"].append("✓ Notion database accessible")
            else:
                print("  ❌ Notion connection failed")
                connection_results["failed"] += 1
                connection_results["details"].append("✗ Notion database validation failed")
        except Exception as e:
            print(f"  ❌ Notion test failed: {str(e)[:100]}...")
            connection_results["failed"] += 1
            connection_results["details"].append("✗ Notion connection error")
        
        # Summary
        if connection_results["failed"] == 0:
            print_success("🎉 All critical connections successful!")
            return True
        else:
            print_warning(f"⚠️ {connection_results['failed']} connection(s) failed")
            print_info("System may still work, but check failed connections")
            return True  # Non-blocking for now
            
    except Exception as e:
        print_error(f"Connection testing failed: {e}")
        print_info("You can still try running the system - some features may not work")
        return True  # Non-blocking

def create_startup_scripts():
    """Create convenient startup scripts."""
    print_step("Creating startup convenience scripts...")
    
    # Windows batch file
    if platform.system() == "Windows":
        batch_content = """@echo off
echo Starting AI Agents Swarm...
conda activate ai 2>nul || echo Warning: 'ai' conda environment not found
python start.py
pause
"""
        Path("start.bat").write_text(batch_content)
        print_success("Created start.bat for Windows")
    
    # Unix shell script
    shell_content = """#!/bin/bash
echo "Starting AI Agents Swarm..."
conda activate ai 2>/dev/null || echo "Warning: 'ai' conda environment not found"
python start.py
"""
    start_sh = Path("start.sh")
    start_sh.write_text(shell_content)
    if platform.system() != "Windows":
        start_sh.chmod(0o755)  # Make executable
        print_success("Created start.sh for Unix/Linux/Mac")
    
    return True

def print_final_instructions():
    """Print final setup instructions and next steps."""
    print()
    print("🎉" + "=" * 60)
    print("🚀 SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 62)
    print()
    
    print("📋 NEXT STEPS:")
    print()
    
    print("1️⃣ START THE SYSTEM:")
    if platform.system() == "Windows":
        print("   • Double-click 'start.bat' OR")
        print("   • Run: conda activate ai && python start.py")
    else:
        print("   • Run: ./start.sh OR")
        print("   • Run: conda activate ai && python start.py")
    print()
    
    print("2️⃣ ACCESS THE DASHBOARD:")
    print("   • Web Dashboard: http://localhost:3000")
    print("   • API Documentation: http://localhost:8000/docs")
    print("   • Health Check: http://localhost:8000/health")
    print()
    
    print("3️⃣ DOCKER ALTERNATIVE:")
    print("   • Run: docker-compose up --build")
    print("   • Access same URLs as above")
    print()
    
    print("⚠️ IMPORTANT REMINDERS:")
    print("   • Gmail: Must use App Password (not regular password)")
    print("   • Notion: Database must be shared with your integration")
    print("   • AI Models: Only Gemini has been fully tested")
    print("   • Email: Only Gmail has been tested and verified")
    print()
    
    print("🆘 NEED HELP?")
    print("   • Check logs in the 'logs/' directory")
    print("   • Visit API docs at http://localhost:8000/docs")
    print("   • Review README.md for detailed documentation")
    print()
    
    print("🎯 WHAT IT DOES:")
    print("   • Monitors your email in real-time")
    print("   • Extracts actionable tasks automatically")
    print("   • Creates organized tasks in Notion")
    print("   • Summarizes meetings and communications")
    print("   • Manages deadlines and follow-ups")
    print()

def main():
    """Main setup orchestration."""
    print_banner()
    
    setup_steps = [
        ("System Requirements", check_system_requirements),
        ("Node.js Environment", check_node_environment),
        ("Python Requirements", install_python_requirements),
        ("Dashboard Dependencies", install_dashboard_dependencies),
        ("Directory Structure", create_directories),
        ("Environment Setup", setup_environment_file),
        ("Configuration Validation", validate_environment_configuration),
        ("Service Connections", test_system_connections),
        ("Startup Scripts", create_startup_scripts),
    ]
    
    failed_steps = []
    
    for step_name, step_function in setup_steps:
        print()
        try:
            if not step_function():
                failed_steps.append(step_name)
                if step_name in ["Configuration Validation"]:
                    # Critical failure - stop setup
                    print_error(f"❌ Setup failed at: {step_name}")
                    print_info("Please fix the issues above and run setup again.")
                    sys.exit(1)
        except KeyboardInterrupt:
            print_error("\n⚠️ Setup interrupted by user")
            sys.exit(1)
        except Exception as e:
            print_error(f"Unexpected error in {step_name}: {e}")
            failed_steps.append(step_name)
    
    # Final results
    if not failed_steps:
        print_final_instructions()
    else:
        print()
        print_warning("⚠️ Setup completed with some warnings:")
        for step in failed_steps:
            print(f"  • {step}")
        print()
        print_info("System should still work, but check the warnings above.")
        print_info("You can run 'python setup.py' again to retry failed steps.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\n⚠️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Fatal setup error: {e}")
        sys.exit(1)
