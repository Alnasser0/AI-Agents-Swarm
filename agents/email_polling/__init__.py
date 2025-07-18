"""
Email polling agent for AI Agents Swarm.

This agent monitors email inboxes for new messages and extracts
task information using AI. It supports IMAP-compatible email providers
like Gmail, Outlook, and others.

Key features:
- Automatic email polling
- Task extraction from email content
- Duplicate detection
- Configurable polling intervals
"""

import imaplib
import email
import email.header
import email.utils
import email.message
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
import pickle
import asyncio
import time

# Internal imports (will work after pip install)
from agents.core import BaseAgent, Task, TaskPriority, get_task_extractor
from config.settings import settings


@dataclass
class EmailMessage:
    """Represents an email message with relevant metadata."""
    subject: str
    sender: str
    content: str
    date: datetime
    message_id: str
    is_unread: bool = True


class EmailAgent(BaseAgent):
    """
    Email polling agent that monitors inbox and extracts tasks.
    
    This agent connects to email servers via IMAP, processes new messages,
    and uses AI to identify and extract task information.
    """
    
    def __init__(self):
        """Initialize the email agent with configuration from settings."""
        super().__init__(name="EmailAgent")
        self.email_address = settings.email_address
        self.email_password = settings.email_password
        self.imap_server = settings.email_imap_server
        self.imap_port = settings.email_imap_port
        self.check_interval = settings.email_check_interval
        
        # Track processed emails to avoid duplicates
        self.processed_emails_file = Path("data/processed_emails.pkl")
        self.processed_emails = self._load_processed_emails()
        
        self.logger.info(f"Email agent configured for {self.email_address}")
    
    def _load_processed_emails(self) -> set:
        """Load the set of already processed email IDs."""
        if self.processed_emails_file.exists():
            try:
                with open(self.processed_emails_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                self.log_error(e, "Loading processed emails")
                return set()
        return set()
    
    def _save_processed_emails(self) -> None:
        """Save the set of processed email IDs."""
        self.processed_emails_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.processed_emails_file, 'wb') as f:
                pickle.dump(self.processed_emails, f)
        except Exception as e:
            self.log_error(e, "Saving processed emails")
    
    def connect_to_email(self) -> imaplib.IMAP4_SSL:
        """
        Connect to the email server and return IMAP connection.
        
        Returns:
            IMAP4_SSL connection object
            
        Raises:
            Exception: If connection fails
        """
        try:
            self.logger.info(f"Connecting to {self.imap_server}:{self.imap_port}")
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_address, self.email_password)
            mail.select('inbox')
            self.logger.info("Successfully connected to email server")
            return mail
        except Exception as e:
            self.log_error(e, "Connecting to email server")
            raise
    
    def fetch_new_emails(self, since_days: int = 1) -> List[EmailMessage]:
        """
        Fetch new emails from the inbox.
        
        Args:
            since_days: Number of days back to check for emails
            
        Returns:
            List of EmailMessage objects
        """
        try:
            mail = self.connect_to_email()
            
            # Search for unread emails from the last N days
            since_date = (datetime.now() - timedelta(days=since_days)).strftime('%d-%b-%Y')
            search_criteria = f'(UNSEEN SINCE {since_date})'
            
            status, messages = mail.search(None, search_criteria)
            if status != 'OK':
                self.logger.warning(f"Email search failed: {status}")
                mail.close()
                return []
            
            email_ids = messages[0].split()
            self.logger.info(f"Found {len(email_ids)} new emails")
            
            emails = []
            for email_id in email_ids:
                try:
                    email_msg = self._parse_email(mail, email_id)
                    if email_msg and email_msg.message_id not in self.processed_emails:
                        emails.append(email_msg)
                except Exception as e:
                    self.log_error(e, f"Parsing email {email_id}")
                    continue
            
            mail.close()
            return emails
                
        except Exception as e:
            self.log_error(e, "Fetching new emails")
            return []
    
    def _parse_email(self, mail: imaplib.IMAP4_SSL, email_id: bytes) -> Optional[EmailMessage]:
        """
        Parse an individual email message.
        
        Args:
            mail: IMAP connection
            email_id: Email ID to fetch
            
        Returns:
            EmailMessage object or None if parsing fails
        """
        try:
            status, msg_data = mail.fetch(email_id.decode(), '(RFC822)')
            if status != 'OK' or not msg_data or not msg_data[0]:
                return None
            
            # msg_data[0] is a tuple: (message_part, data)
            email_body = msg_data[0][1]
            if not email_body or not isinstance(email_body, bytes):
                return None
                
            import email as email_module
            email_message = email_module.message_from_bytes(email_body)
            
            # Extract basic information
            subject = self._decode_header(email_message.get('Subject', ''))
            sender = self._decode_header(email_message.get('From', ''))
            date_str = email_message.get('Date', '')
            message_id = email_message.get('Message-ID', '')
            
            # Parse date
            try:
                import email.utils
                date = email.utils.parsedate_to_datetime(date_str)
            except:
                date = datetime.now()
            
            # Extract content
            content = self._extract_email_content(email_message)
            
            return EmailMessage(
                subject=subject,
                sender=sender,
                content=content,
                date=date,
                message_id=message_id,
                is_unread=True
            )
            
        except Exception as e:
            self.log_error(e, f"Parsing email {email_id}")
            return None
    
    def _decode_header(self, header: str) -> str:
        """Decode email header handling various encodings."""
        if not header:
            return ''
        
        decoded_parts = []
        for part, encoding in email.header.decode_header(header):
            if isinstance(part, bytes):
                part = part.decode(encoding or 'utf-8', errors='ignore')
            decoded_parts.append(part)
        
        return ''.join(decoded_parts)
    
    def _extract_email_content(self, email_message: email.message.Message) -> str:
        """Extract text content from email message."""
        content = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload and isinstance(payload, bytes):
                        content += payload.decode('utf-8', errors='ignore')
        else:
            payload = email_message.get_payload(decode=True)
            if payload and isinstance(payload, bytes):
                content = payload.decode('utf-8', errors='ignore')
        
        return content.strip()
    
    async def extract_tasks_from_email(self, email_msg: EmailMessage) -> Optional[Task]:
        """
        Extract task information from an email using AI.
        
        Args:
            email_msg: Email message to analyze
            
        Returns:
            Task object if a task is found, None otherwise
        """
        try:
            # Combine subject and content for analysis
            full_text = f"Subject: {email_msg.subject}\n\nContent:\n{email_msg.content}"
            
            # Use AI to extract task information
            result = await get_task_extractor().run(full_text)
            extracted = result.output
            
            self.logger.info(f"Task extraction result: confidence={extracted.confidence}, is_task={extracted.is_task}")
            
            # Only create task if confidence is high enough
            if extracted.is_task and extracted.confidence >= 0.7:
                # Parse due date if provided
                due_date = None
                if extracted.due_date:
                    try:
                        due_date = datetime.strptime(extracted.due_date, '%Y-%m-%d')
                    except ValueError:
                        self.logger.warning(f"Invalid due date format: {extracted.due_date}")
                
                task = Task(
                    title=extracted.title,
                    description=extracted.description,
                    priority=extracted.priority,
                    source="email",
                    source_id=email_msg.message_id,
                    due_date=due_date,
                    tags=extracted.tags,
                    metadata={
                        "sender": email_msg.sender,
                        "subject": email_msg.subject,
                        "confidence": extracted.confidence,
                        "email_date": email_msg.date.isoformat()
                    }
                )
                
                self.log_task_processed(task)
                return task
            
            return None
            
        except Exception as e:
            self.log_error(e, f"Extracting tasks from email {email_msg.message_id}")
            return None
    
    async def process_new_emails(self) -> List[Task]:
        """
        Process new emails and extract tasks.
        
        Returns:
            List of extracted tasks
        """
        self.logger.info("Starting email processing")
        
        # Fetch new emails
        new_emails = self.fetch_new_emails()
        if not new_emails:
            self.logger.info("No new emails to process")
            return []
        
        # Process each email
        tasks = []
        for email_msg in new_emails:
            try:
                task = await self.extract_tasks_from_email(email_msg)
                if task:
                    tasks.append(task)
                
                # Mark email as processed
                self.processed_emails.add(email_msg.message_id)
                
            except Exception as e:
                self.log_error(e, f"Processing email {email_msg.message_id}")
                continue
        
        # Save processed emails
        self._save_processed_emails()
        
        self.logger.info(f"Processed {len(new_emails)} emails, extracted {len(tasks)} tasks")
        return tasks
    
    def start_polling(self) -> None:
        """Start the email polling loop."""
        self.logger.info(f"Starting email polling every {self.check_interval} seconds")
        
        while True:
            try:
                tasks = asyncio.run(self.process_new_emails())
                if tasks:
                    self.logger.info(f"Found {len(tasks)} new tasks")
                    # Tasks will be processed by the main orchestrator
                
            except Exception as e:
                self.log_error(e, "Email polling loop")
            
            # Wait before next check
            time.sleep(self.check_interval)
