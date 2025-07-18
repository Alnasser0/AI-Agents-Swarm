"""
Example scripts for AI Agents Swarm.

This directory contains example scripts showing how to use the system
programmatically and extend it with custom functionality.
"""

import asyncio
from datetime import datetime

# Example 1: Manual email processing
async def example_email_processing():
    """Example of manual email processing."""
    from agents.email_polling import EmailAgent
    
    agent = EmailAgent()
    
    # Process new emails
    tasks = await agent.process_new_emails()
    
    print(f"Found {len(tasks)} new tasks:")
    for task in tasks:
        print(f"- {task.title} (Priority: {task.priority})")


# Example 2: Create task manually
def example_create_task():
    """Example of creating a task manually."""
    from agents.notion_integration import NotionAgent
    from agents.core import Task, TaskPriority
    
    agent = NotionAgent()
    
    task = Task(
        title="Example Task",
        description="This is an example task created programmatically",
        priority=TaskPriority.HIGH,
        source="example_script",
        tags=["example", "demo"],
        metadata={"created_by": "example_script"}
    )
    
    page_id = agent.create_task_in_notion(task)
    
    if page_id:
        print(f"Task created successfully: {page_id}")
    else:
        print("Failed to create task")


# Example 3: Full pipeline
async def example_full_pipeline():
    """Example of running the full pipeline."""
    from agents.main import AgentOrchestrator
    
    orchestrator = AgentOrchestrator()
    
    # Run the email-to-notion pipeline
    await orchestrator.process_email_to_notion_pipeline()
    
    # Get stats
    stats = orchestrator.get_system_stats()
    print(f"Pipeline stats: {stats}")


# Example 4: Custom agent extension
class CustomAgent:
    """Example of how to create a custom agent."""
    
    def __init__(self):
        self.name = "CustomAgent"
        print(f"Initialized {self.name}")
    
    def process_custom_data(self, data):
        """Process custom data and return tasks."""
        # This would contain your custom logic
        print(f"Processing custom data: {data}")
        return []


if __name__ == "__main__":
    print("AI Agents Swarm - Examples")
    print("=" * 40)
    
    # Run email processing example
    print("\n1. Email Processing Example:")
    asyncio.run(example_email_processing())
    
    # Run task creation example
    print("\n2. Task Creation Example:")
    example_create_task()
    
    # Run full pipeline example
    print("\n3. Full Pipeline Example:")
    asyncio.run(example_full_pipeline())
    
    # Show custom agent example
    print("\n4. Custom Agent Example:")
    custom_agent = CustomAgent()
    custom_agent.process_custom_data("example data")
