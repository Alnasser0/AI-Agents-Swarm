#!/usr/bin/env python3
"""
Simple test to run the email processing pipeline once.
"""

import asyncio
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from agents.main import AgentOrchestrator

async def test_pipeline():
    """Test the email processing pipeline."""
    print("🤖 Testing AI Agents Swarm Pipeline")
    print("=" * 50)
    
    try:
        # Initialize orchestrator
        print("Initializing orchestrator...")
        orchestrator = AgentOrchestrator()
        
        # Run single cycle
        print("Running single cycle...")
        await orchestrator.run_single_cycle()
        
        # Get stats
        stats = orchestrator.get_system_stats()
        print(f"\n📊 Results:")
        print(f"   Tasks processed: {stats['tasks_processed']}")
        print(f"   Emails processed: {stats['emails_processed']}")
        print(f"   Errors: {stats['errors']}")
        
        if stats['tasks_processed'] > 0:
            print("✅ Success! Tasks were created in Notion.")
        else:
            print("⚠️  No tasks were processed. Check if there are unread emails with task requests.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pipeline())
