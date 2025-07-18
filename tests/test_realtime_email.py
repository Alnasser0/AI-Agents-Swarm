#!/usr/bin/env python3
"""
Test script for real-time email processing.

This script tests the new real-time email processing capabilities including:
- IMAP IDLE support detection
- Webhook endpoint functionality
- Integration with the orchestrator
"""

import asyncio
import time
import requests
from datetime import datetime

from agents.main import AgentOrchestrator
from config.settings import settings


async def test_realtime_email_processing():
    """Test real-time email processing functionality."""
    print("🚀 Testing Real-time Email Processing")
    print("=" * 50)
    
    try:
        # Initialize orchestrator
        print("1. Initializing orchestrator...")
        orchestrator = AgentOrchestrator()
        
        # Check IMAP IDLE support
        print("2. Checking IMAP IDLE support...")
        if orchestrator.realtime_processor.is_idle_supported():
            print("   ✅ IMAP IDLE is supported")
        else:
            print("   ❌ IMAP IDLE is NOT supported (will use polling only)")
        
        # Get initial stats
        print("3. Getting system stats...")
        stats = orchestrator.get_system_stats()
        print(f"   📊 Initial stats: {stats.get('realtime_email', {})}")
        
        # Test webhook processing
        print("4. Testing webhook processing...")
        test_webhook_data = {
            "provider": "gmail",
            "event": "new_email",
            "timestamp": datetime.now().isoformat(),
            "test": True
        }
        
        # Test the webhook callback directly
        orchestrator.realtime_processor.process_webhook_notification(test_webhook_data)
        print("   ✅ Webhook processing completed")
        
        # Test real-time monitoring (short duration)
        print("5. Testing real-time monitoring...")
        orchestrator.start_realtime_monitoring()
        
        # Wait a bit to see if monitoring starts
        await asyncio.sleep(3)
        
        # Get updated stats
        stats = orchestrator.get_system_stats()
        realtime_status = stats.get('realtime_email', {})
        print(f"   📊 Real-time status: {realtime_status}")
        
        # Stop monitoring
        orchestrator.stop_realtime_monitoring()
        print("   ✅ Real-time monitoring stopped")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


def test_webhook_endpoint():
    """Test the webhook endpoint via HTTP."""
    print("\n🌐 Testing Webhook Endpoint")
    print("=" * 30)
    
    try:
        # Test data
        test_data = {
            "provider": "gmail",
            "event": "new_email",
            "timestamp": datetime.now().isoformat(),
            "test": True
        }
        
        # Make request to webhook endpoint
        url = f"http://{settings.api_host}:{settings.api_port}/webhook/email/test"
        print(f"Making request to: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Webhook endpoint responded successfully")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Webhook endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running.")
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")


if __name__ == "__main__":
    print("🔧 Real-time Email Processing Test Suite")
    print("=" * 50)
    
    # Run async test
    asyncio.run(test_realtime_email_processing())
    
    # Run webhook test
    test_webhook_endpoint()
    
    print("\n✅ Test suite completed!")
