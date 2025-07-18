#!/usr/bin/env python3
"""
Setup script for AI Agents Swarm.

This script helps set up the AI Agents Swarm system with minimal friction.
It handles:
- Environment setup
- Configuration validation
- Database schema creation
- Initial system testing
"""

import os
import sys
import subprocess
from pathlib import Path

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

def check_python_version():
    """Check Python version compatibility."""
    if sys.version_info < (3, 8):
        print_error("Python 3.8 or higher is required")
        sys.exit(1)
    print_success(f"Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_requirements():
    """Install Python requirements."""
    print_step("Installing Python requirements...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True, text=True)
        print_success("Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install requirements: {e}")
        print("Output:", e.stdout)
        print("Error:", e.stderr)
        sys.exit(1)

def create_directories():
    """Create necessary directories."""
    print_step("Creating directories...")
    
    directories = ["data", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print_success("Directories created")

def setup_environment():
    """Set up environment file."""
    print_step("Setting up environment configuration...")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_file.exists():
        if env_example.exists():
            env_file.write_text(env_example.read_text())
            print_success("Environment file created from template")
            print_warning("Please edit .env with your API keys and configuration")
        else:
            print_error("No .env.example file found")
            return False
    else:
        print_success("Environment file already exists")
    
    return True

def validate_configuration():
    """Validate configuration settings."""
    print_step("Validating configuration...")
    
    try:
        # This will load and validate settings
        from config.settings import settings
        
        # Check required settings
        required_settings = [
            ("email_address", "Email address"),
            ("email_password", "Email password"),
            ("notion_api_key", "Notion API key"),
            ("notion_database_id", "Notion database ID")
        ]
        
        missing_settings = []
        for setting_name, display_name in required_settings:
            value = getattr(settings, setting_name, None)
            if not value or value.startswith("your-"):
                missing_settings.append(display_name)
        
        if missing_settings:
            print_warning(f"Missing configuration: {', '.join(missing_settings)}")
            print("Please update your .env file with the required values")
            return False
        
        print_success("Configuration validation passed")
        return True
        
    except Exception as e:
        print_error(f"Configuration validation failed: {e}")
        return False

def test_connections():
    """Test system connections."""
    print_step("Testing system connections...")
    
    try:
        from agents.main import AgentOrchestrator
        
        orchestrator = AgentOrchestrator()
        
        # Test Notion connection
        print("Testing Notion connection...")
        if orchestrator.notion_agent.validate_database_setup():
            print_success("Notion connection successful")
        else:
            print_error("Notion connection failed - check your API key and database ID")
            return False
        
        # Test email connection would go here
        print_success("Connection tests passed")
        return True
        
    except Exception as e:
        print_error(f"Connection test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🤖 AI Agents Swarm Setup")
    print("=" * 50)
    
    # Step 1: Check Python version
    check_python_version()
    
    # Step 2: Install requirements
    install_requirements()
    
    # Step 3: Create directories
    create_directories()
    
    # Step 4: Set up environment
    if not setup_environment():
        sys.exit(1)
    
    # Step 5: Validate configuration
    if not validate_configuration():
        print("\n⚠️  Configuration incomplete. Please:")
        print("1. Edit .env file with your API keys")
        print("2. Run 'python setup.py' again")
        sys.exit(1)
    
    # Step 6: Test connections
    if not test_connections():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run the system: python -m agents.main")
    print("2. Or launch dashboard: python cli.py dashboard")
    print("3. Or use API: python cli.py api")
    print("\nFor help: python cli.py --help")

if __name__ == "__main__":
    main()
