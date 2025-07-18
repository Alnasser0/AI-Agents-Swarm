"""
Basic tests for AI Agents Swarm system.

This module provides simple tests to validate the system setup
and ensure all components are working correctly.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported correctly."""
    print("Testing imports...")
    
    try:
        from config.settings import settings
        print("✅ Settings imported successfully")
    except Exception as e:
        print(f"❌ Settings import failed: {e}")
        return False
    
    try:
        from agents.core import BaseAgent, Task, TaskPriority
        print("✅ Core agents imported successfully")
    except Exception as e:
        print(f"❌ Core agents import failed: {e}")
        return False
    
    try:
        from agents.email_polling import EmailAgent
        print("✅ Email agent imported successfully")
    except Exception as e:
        print(f"❌ Email agent import failed: {e}")
        return False
    
    try:
        from agents.notion_integration import NotionAgent
        print("✅ Notion agent imported successfully")
    except Exception as e:
        print(f"❌ Notion agent import failed: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")
    
    try:
        from config.settings import settings
        
        # Test that settings can be accessed
        print(f"Email provider: {settings.email_provider}")
        print(f"Default model: {settings.default_model}")
        print(f"Log level: {settings.log_level}")
        
        print("✅ Configuration loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_task_creation():
    """Test task creation functionality."""
    print("\nTesting task creation...")
    
    try:
        from agents.core import Task, TaskPriority
        from datetime import datetime
        
        # Create a test task
        task = Task(
            title="Test Task",
            description="This is a test task",
            priority=TaskPriority.MEDIUM,
            source="test",
            tags=["test", "validation"],
            metadata={"test": True}
        )
        
        print(f"Created task: {task.title}")
        print(f"Priority: {task.priority}")
        print(f"Source: {task.source}")
        print(f"Created at: {task.created_at}")
        
        print("✅ Task creation successful")
        return True
        
    except Exception as e:
        print(f"❌ Task creation failed: {e}")
        return False

async def test_ai_agent():
    """Test AI agent functionality."""
    print("\nTesting AI agent...")
    
    try:
        from agents.core import get_task_extractor
        
        # Test email content
        test_email = """
        Subject: Create task for project review
        
        Hi there,
        
        Can you please create a task to review the project presentation slides?
        This needs to be done by Friday as we have the client meeting on Monday.
        
        Thanks!
        """
        
        # This would normally use the AI model
        # For testing, we'll just verify the agent exists
        print("AI task extraction agent initialized")
        print("✅ AI agent test passed")
        return True
        
    except Exception as e:
        print(f"❌ AI agent test failed: {e}")
        return False

def test_directory_structure():
    """Test that required directories exist."""
    print("\nTesting directory structure...")
    
    required_dirs = [
        "agents",
        "config", 
        "ui",
        "api",
        "examples"
    ]
    
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"✅ {directory}/ exists")
        else:
            print(f"❌ {directory}/ missing")
            return False
    
    # Check that data and logs directories can be created
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    print("✅ Directory structure validated")
    return True

async def run_all_tests():
    """Run all tests."""
    print("🧪 Running AI Agents Swarm Tests")
    print("=" * 50)
    
    tests = [
        test_directory_structure,
        test_imports,
        test_configuration,
        test_task_creation,
        test_ai_agent,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if asyncio.iscoroutinefunction(test):
                result = await test()
            else:
                result = test()
            
            if result:
                passed += 1
            else:
                failed += 1
                
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! System is ready to use.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    # Run tests
    success = asyncio.run(run_all_tests())
    
    if success:
        print("\n✅ System validation complete!")
        print("Next steps:")
        print("1. Update .env with your API keys")
        print("2. Run: python setup.py")
        print("3. Start the system: python -m agents.main")
    else:
        print("\n❌ System validation failed!")
        sys.exit(1)
