"""
Notion integration agent for AI Agents Swarm.

This agent handles creating and managing tasks in Notion databases.
It provides a simple interface to push tasks from various sources
into Notion with proper formatting and metadata.

Key features:
- Create tasks in Notion databases
- Update task status and properties
- Handle different task types and priorities
- Rich formatting support
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from notion_client import Client
from notion_client.errors import APIResponseError

# Internal imports
from agents.core import BaseAgent, Task, TaskPriority, TaskStatus
from config.settings import settings


class NotionAgent(BaseAgent):
    """
    Notion integration agent for task management.
    
    This agent creates and manages tasks in Notion databases,
    providing a clean interface between the AI agents and Notion.
    """
    
    def __init__(self, model: Optional[str] = None):
        """Initialize the Notion agent with API credentials."""
        super().__init__(name="NotionAgent", model=model)
        self.client = Client(auth=settings.notion_api_key)
        self.database_id = settings.notion_database_id
        
        # Test connection
        try:
            self.client.databases.retrieve(database_id=self.database_id)
            self.logger.info("Successfully connected to Notion database")
        except APIResponseError as e:
            self.log_error(e, "Connecting to Notion database")
            raise
    
    def _priority_to_notion_select(self, priority: TaskPriority) -> str:
        """Convert TaskPriority enum to Notion select option."""
        priority_map = {
            TaskPriority.LOW: "Low",
            TaskPriority.MEDIUM: "Medium", 
            TaskPriority.HIGH: "High",
            TaskPriority.URGENT: "High"  # Map urgent to high since your DB doesn't have urgent
        }
        return priority_map.get(priority, "Medium")
    
    def _status_to_notion_select(self, status: TaskStatus) -> str:
        """Convert TaskStatus enum to Notion select option."""
        status_map = {
            TaskStatus.TODO: "Not started",
            TaskStatus.IN_PROGRESS: "In progress",
            TaskStatus.DONE: "Done",
            TaskStatus.CANCELLED: "Not started"  # Map cancelled to not started
        }
        return status_map.get(status, "Not started")
    
    def _task_exists(self, task: Task) -> bool:
        """
        Check if a task with the same title already exists in Notion.
        
        Args:
            task: Task to check for duplicates
            
        Returns:
            True if task exists, False otherwise
        """
        try:
            # Query the database for tasks with the same title
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Task name",
                    "title": {
                        "equals": task.title
                    }
                }
            )
            
            # If any results are returned, the task exists
            results = response.get("results", [])
            if results:
                self.logger.info(f"Found {len(results)} existing tasks with title: {task.title}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking for duplicate task: {e}")
            # If we can't check, assume it doesn't exist to avoid blocking task creation
            return False
    
    def create_task_in_notion(self, task: Task) -> Optional[str]:
        """
        Create a new task in the Notion database.
        
        Args:
            task: Task object to create in Notion
            
        Returns:
            Notion page ID if successful, None otherwise
        """
        try:
            # Check for duplicate tasks first
            if self._task_exists(task):
                self.logger.warning(f"Task '{task.title}' already exists in Notion, skipping creation")
                return None
            
            # Prepare the page properties to match your database schema
            properties = {
                "Task name": {
                    "title": [
                        {
                            "text": {
                                "content": task.title
                            }
                        }
                    ]
                },
                "Status": {
                    "status": {
                        "name": self._status_to_notion_select(task.status)
                    }
                },
                "Priority": {
                    "select": {
                        "name": self._priority_to_notion_select(task.priority)
                    }
                },
                "Description": {
                    "rich_text": [
                        {
                            "text": {
                                "content": task.description
                            }
                        }
                    ]
                },
                "Task type": {
                    "multi_select": [
                        {
                            "name": "💬 Feature request"  # Default task type as multi_select
                        }
                    ]
                },
                "Effort level": {
                    "select": {
                        "name": "Medium"  # Default effort level
                    }
                }
            }
            
            # Add due date if provided
            if task.due_date:
                properties["Due date"] = {
                    "date": {
                        "start": task.due_date.isoformat()
                    }
                }
            
            # Create the page with minimal content since we have description in properties
            children = []
            
            # Add source information as content
            if task.source:
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"Source: {task.source}"
                                }
                            }
                        ]
                    }
                })
            
            # Add metadata if available
            if task.metadata:
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"Metadata: {task.metadata}"
                                }
                            }
                        ]
                    }
                })
            if task.metadata:
                children.append({
                    "object": "block",
                    "type": "toggle",
                    "toggle": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "Metadata"
                                }
                            }
                        ],
                        "children": [
                            {
                                "object": "block",
                                "type": "code",
                                "code": {
                                    "language": "json",
                                    "rich_text": [
                                        {
                                            "type": "text",
                                            "text": {
                                                "content": str(task.metadata)
                                            }
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                })
            
            # Create the page
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties,
                children=children
            )
            
            page_id = response["id"]
            self.logger.info(f"Created Notion task: {task.title} (ID: {page_id})")
            return page_id
            
        except APIResponseError as e:
            self.log_error(e, f"Creating Notion task: {task.title}")
            return None
    
    def update_task_status(self, page_id: str, status: TaskStatus) -> bool:
        """
        Update a task's status in Notion.
        
        Args:
            page_id: Notion page ID
            status: New task status
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.pages.update(
                page_id=page_id,
                properties={
                    "Status": {
                        "status": {
                            "name": self._status_to_notion_select(status)
                        }
                    }
                }
            )
            self.logger.info(f"Updated task status to {status.value}")
            return True
            
        except APIResponseError as e:
            self.log_error(e, f"Updating task status: {page_id}")
            return False
    
    async def batch_create_tasks(self, tasks: List[Task]) -> List[Optional[str]]:
        """
        Create multiple tasks in Notion efficiently.
        
        Args:
            tasks: List of Task objects to create
            
        Returns:
            List of Notion page IDs (None for failed creations)
        """
        page_ids = []
        
        for task in tasks:
            try:
                page_id = self.create_task_in_notion(task)
                page_ids.append(page_id)
                
                # Small delay to respect rate limits
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.log_error(e, f"Batch creating task: {task.title}")
                page_ids.append(None)
        
        successful_creates = len([pid for pid in page_ids if pid is not None])
        self.logger.info(f"Batch created {successful_creates}/{len(tasks)} tasks")
        
        return page_ids
    
    def search_tasks_by_source(self, source: str, source_id: str) -> List[Dict[str, Any]]:
        """
        Search for tasks by source and source ID to avoid duplicates.
        
        Args:
            source: Source system (email, slack, etc.)
            source_id: Source-specific identifier
            
        Returns:
            List of matching Notion pages
        """
        try:
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "and": [
                        {
                            "property": "Source",
                            "select": {
                                "equals": source.title()
                            }
                        }
                    ]
                }
            )
            
            # Filter by source_id in metadata (would need custom property)
            # For now, return all matching source tasks
            return response.get("results", [])
            
        except APIResponseError as e:
            self.log_error(e, f"Searching tasks by source: {source}")
            return []
    
    def get_database_schema(self) -> Dict[str, Any]:
        """
        Get the current database schema for validation.
        
        Returns:
            Database schema information
        """
        try:
            response = self.client.databases.retrieve(database_id=self.database_id)
            return response.get("properties", {})
            
        except APIResponseError as e:
            self.log_error(e, "Getting database schema")
            return {}
    
    def validate_database_setup(self) -> bool:
        """
        Validate that the Notion database has the required properties.
        
        Returns:
            True if database is properly configured
        """
        try:
            schema = self.get_database_schema()
            
            # Updated to match your Tasks Tracker database schema with correct property types
            required_properties = {
                "Task name": "title",
                "Status": "status",  # Notion uses "status" type, not "select"
                "Priority": "select",
                "Description": "rich_text"
            }
            
            for prop_name, prop_type in required_properties.items():
                if prop_name not in schema:
                    self.logger.error(f"Missing required property: {prop_name}")
                    return False
                    
                if schema[prop_name]["type"] != prop_type:
                    self.logger.error(f"Property {prop_name} has wrong type. Expected {prop_type}, got {schema[prop_name]['type']}")
                    return False
            
            self.logger.info("Database schema validation passed")
            return True
            
        except Exception as e:
            self.log_error(e, "Validating database setup")
            return False

    def get_recent_tasks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent tasks from Notion database."""
        try:
            # Query the database for recent tasks, sorted by creation time
            # Use Notion's built-in created_time instead of "Created time" property
            response = self.client.databases.query(
                database_id=self.database_id,
                sorts=[
                    {
                        "timestamp": "created_time",
                        "direction": "descending"
                    }
                ],
                page_size=limit
            )
            
            tasks = []
            results = response.get("results", [])
            
            for result in results:
                try:
                    properties = result.get("properties", {})
                    
                    # Extract task information using proper Notion property access
                    task = {
                        "id": result.get("id", ""),
                        "title": self._extract_title(properties.get("Task name", {})),
                        "source": self._extract_rich_text(properties.get("Source", {})),
                        "priority": self._extract_select(properties.get("Priority", {})),
                        "status": self._extract_select(properties.get("Status", {})),
                        "from": self._extract_rich_text(properties.get("From", {})),
                        "created": self._extract_date(result.get("created_time", ""))
                    }
                    tasks.append(task)
                except Exception as e:
                    self.logger.warning(f"Error parsing task: {e}")
                    continue
            
            return tasks
            
        except Exception as e:
            self.log_error(e, "Getting recent tasks")
            return []
    
    def _extract_title(self, title_prop: Dict[str, Any]) -> str:
        """Extract title from Notion title property."""
        try:
            return title_prop.get("title", [{}])[0].get("plain_text", "Untitled")
        except (IndexError, KeyError):
            return "Untitled"
    
    def _extract_rich_text(self, text_prop: Dict[str, Any]) -> str:
        """Extract text from Notion rich text property."""
        try:
            return text_prop.get("rich_text", [{}])[0].get("plain_text", "")
        except (IndexError, KeyError):
            return ""
    
    def _extract_select(self, select_prop: Dict[str, Any]) -> str:
        """Extract value from Notion select property."""
        try:
            return select_prop.get("select", {}).get("name", "")
        except KeyError:
            return ""
    
    def _extract_date(self, date_value: str) -> str:
        """Extract and format date string."""
        try:
            if date_value:
                return date_value
            return datetime.now().isoformat()
        except:
            return datetime.now().isoformat()
