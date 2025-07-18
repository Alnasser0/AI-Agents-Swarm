#!/usr/bin/env python3
"""Troubleshooting script for the AI Agents Swarm system."""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_environment():
    """Check if all required environment variables are set."""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        'EMAIL_ADDRESS',
        'EMAIL_PASSWORD',
        'NOTION_DATABASE_ID',
        'NOTION_TOKEN'
    ]
    
    optional_vars = [
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY',
        'GOOGLE_API_KEY'
    ]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"✅ {var} is set")
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
        else:
            print(f"✅ {var} is set")
    
    if missing_required:
        print(f"❌ Missing required variables: {missing_required}")
        return False
    
    if missing_optional:
        print(f"⚠️  Missing optional variables: {missing_optional}")
        print("At least one AI API key is required for the system to work.")
    
    return True

def check_notion_connection():
    """Check if Notion connection is working."""
    print("\n🔍 Checking Notion connection...")
    
    try:
        from agents.notion_integration import NotionAgent
        
        notion_agent = NotionAgent()
        
        # Test connection by trying to validate the database
        result = notion_agent.validate_database()
        print(f"✅ Notion connection successful! Database validated")
        return True
        
    except Exception as e:
        print(f"❌ Notion connection failed: {e}")
        return False

def check_email_connection():
    """Check if email connection is working."""
    print("\n🔍 Checking email connection...")
    
    try:
        from agents.email_polling import EmailAgent
        
        email_agent = EmailAgent()
        
        # Test connection
        with email_agent.connect_to_email() as mail:
            status, messages = mail.search(None, 'ALL')
            if status == 'OK':
                print(f"✅ Email connection successful! Found {len(messages[0].split())} messages")
                return True
            else:
                print(f"❌ Email search failed: {status}")
                return False
                
    except Exception as e:
        print(f"❌ Email connection failed: {e}")
        return False

def check_ai_model():
    """Check if AI model is available."""
    print("\n🔍 Checking AI model availability...")
    
    try:
        from agents.core import get_best_available_model
        
        model = get_best_available_model()
        print(f"✅ AI model available: {model}")
        return True
        
    except Exception as e:
        print(f"❌ AI model not available: {e}")
        return False

def main():
    """Run all troubleshooting checks."""
    print("🚀 AI Agents Swarm Troubleshooting")
    print("=" * 50)
    
    checks = [
        ("Environment Variables", check_environment),
        ("AI Model", check_ai_model),
        ("Notion Connection", check_notion_connection),
        ("Email Connection", check_email_connection),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 30)
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All checks passed! The system should work correctly.")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above before using the system.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
