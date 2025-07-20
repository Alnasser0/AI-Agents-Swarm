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
    
    def __init__(self, model: Optional[str] = None):
        """Initialize the email agent with configuration from settings."""
        super().__init__(name="EmailAgent", model=model)
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
            self.logger.info(f"Saved {len(self.processed_emails)} processed email IDs")
        except Exception as e:
            self.log_error(e, "Saving processed emails")
    
    def clear_processed_emails(self) -> None:
        """Clear all processed email IDs (for testing/debugging)."""
        self.processed_emails.clear()
        self._save_processed_emails()
        self.logger.info("Cleared all processed email IDs")
    
    def get_processed_email_count(self) -> int:
        """Get the number of processed emails."""
        return len(self.processed_emails)
    
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
    
    def fetch_new_emails(self, since_days: int = 7, limit: int = 50) -> List[EmailMessage]:
        """
        Fetch new emails from the inbox that haven't been processed yet.
        
        Args:
            since_days: Number of days back to check for emails
            limit: Maximum number of emails to process in one batch
            
        Returns:
            List of EmailMessage objects
        """
        try:
            mail = self.connect_to_email()
            
            # Search for all emails from the last N days (not just unread)
            since_date = (datetime.now() - timedelta(days=since_days)).strftime('%d-%b-%Y')
            search_criteria = f'(SINCE {since_date})'
            
            self.logger.info(f"Searching for emails since {since_date} (limit: {limit})")
            
            status, messages = mail.search(None, search_criteria)
            if status != 'OK':
                self.logger.warning(f"Email search failed: {status}")
                mail.close()
                return []
            
            email_ids = messages[0].split()
            
            # Sort email IDs to process newest first (reverse order)
            email_ids = email_ids[::-1]
            
            # Apply limit to email IDs
            if len(email_ids) > limit:
                self.logger.info(f"Found {len(email_ids)} emails, processing latest {limit}")
                email_ids = email_ids[:limit]
            else:
                self.logger.info(f"Found {len(email_ids)} emails, processing all")
            
            emails = []
            processed_count = 0
            
            for email_id in email_ids:
                try:
                    email_msg = self._parse_email(mail, email_id)
                    if email_msg:
                        if email_msg.message_id not in self.processed_emails:
                            emails.append(email_msg)
                            self.logger.info(f"New email found: {email_msg.subject[:50]}...")
                        else:
                            processed_count += 1
                except Exception as e:
                    self.log_error(e, f"Parsing email {email_id}")
                    continue
            
            mail.close()
            
            self.logger.info(f"Found {len(emails)} new emails ({processed_count} already processed)")
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
    
    def _is_automated_email(self, email_msg: EmailMessage) -> bool:
        """
        Check if an email is likely automated/system generated.
        
        Args:
            email_msg: Email message to check
            
        Returns:
            True if email appears to be automated, False otherwise
        """
        # Check sender for automated indicators
        sender_lower = email_msg.sender.lower()
        automated_senders = [
            'noreply@', 'no-reply@', 'donotreply@', 'do-not-reply@',
            'security@', 'alerts@', 'notifications@', 'system@',
            'admin@', 'support@', 'help@', 'info@', 'news@',
            'updates@', 'marketing@', 'promo@', 'newsletter@',
            'accounts@', 'billing@', 'payments@', 'services@'
        ]
        
        if any(indicator in sender_lower for indicator in automated_senders):
            return True
        
        # Check subject for automated indicators
        subject_lower = email_msg.subject.lower()
        automated_subjects = [
            'security alert', 'security warning', 'account alert',
            'password reset', 'login attempt', 'suspicious activity',
            'verify your account', 'confirmation required', 'activate your',
            'welcome to', 'thank you for', 'subscription', 'newsletter',
            'unsubscribe', 'promotion', 'offer', 'deal', 'sale',
            'invoice', 'receipt', 'payment', 'billing', 'statement',
            'notification', 'reminder', 'alert', 'update available',
            'system maintenance', 'service update', 'terms of service'
        ]
        
        if any(indicator in subject_lower for indicator in automated_subjects):
            return True
        
        # Check content for automated indicators
        content_lower = email_msg.content.lower()
        automated_content = [
            'this is an automated message', 'do not reply to this email',
            'this email was sent automatically', 'unsubscribe',
            'click here to verify', 'activate your account',
            'for security reasons', 'suspicious activity detected',
            'please verify your identity', 'account security'
        ]
        
        if any(indicator in content_lower for indicator in automated_content):
            return True
        
        return False
    
    async def extract_tasks_from_email(self, email_msg: EmailMessage) -> Optional[Task]:
        """
        Extract task information from an email using AI with enhanced duplicate prevention.
        
        Args:
            email_msg: Email message to analyze
            
        Returns:
            Task object if a task is found, None otherwise
        """
        try:
            # First check: Skip if email is already processed
            if email_msg.message_id in self.processed_emails:
                self.logger.debug(f"Email already processed, skipping: {email_msg.message_id}")
                return None
            
            # Pre-filter: Skip automated/system emails
            if self._is_automated_email(email_msg):
                self.logger.info(f"Skipping automated email: {email_msg.subject}")
                return None  # Don't mark as processed yet - let process_new_emails handle it
            
            # Combine subject and content for analysis
            full_text = f"Subject: {email_msg.subject}\n\nSender: {email_msg.sender}\n\nContent:\n{email_msg.content}"
            
            # Use AI to extract task information
            result = await get_task_extractor().run(full_text)
            extracted = result.output
            
            self.logger.info(f"Task extraction result: confidence={extracted.confidence}, is_task={extracted.is_task}")
            
            # Only create task if confidence is high enough - be very conservative
            if extracted.is_task and extracted.confidence >= 0.8:  # Raised threshold for human tasks
                # Parse due date if provided
                due_date = None
                if extracted.due_date:
                    try:
                        # Try standard format first
                        due_date = datetime.strptime(extracted.due_date, '%Y-%m-%d')
                    except ValueError:
                        # Try to parse natural language dates
                        try:
                            import dateutil.parser
                            due_date = dateutil.parser.parse(extracted.due_date)
                        except Exception:
                            self.logger.warning(f"Could not parse due date: {extracted.due_date}")
                            # Store as text in metadata for manual review
                            due_date = None
                
                metadata = {
                    "sender": email_msg.sender,
                    "subject": email_msg.subject,
                    "confidence": extracted.confidence,
                    "email_date": email_msg.date.isoformat(),
                    "message_id": email_msg.message_id  # Store for tracking
                }
                
                # Add raw due date if parsing failed
                if extracted.due_date and due_date is None:
                    metadata["raw_due_date"] = extracted.due_date
                
                task = Task(
                    title=extracted.title,
                    description=extracted.description,
                    priority=extracted.priority,
                    source="email",
                    source_id=email_msg.message_id,  # Use message_id for duplicate detection
                    due_date=due_date,
                    tags=extracted.tags,
                    metadata=metadata
                )
                
                # Don't mark as processed here - let the main pipeline do it after successful Notion creation
                self.log_task_processed(task)
                return task
            else:
                self.logger.info(f"Email not identified as task: confidence={extracted.confidence}, is_task={extracted.is_task}")
                self.logger.info(f"Subject: {email_msg.subject}")
                self.logger.info(f"Content preview: {email_msg.content[:200]}...")
                
                # Return None but don't mark as processed yet - let process_new_emails handle it
            
            return None
            
        except Exception as e:
            self.log_error(e, f"Extracting tasks from email {email_msg.message_id}")
            # Don't mark as processed if there was an error - allow retry
            return None
    
    async def process_new_emails(self, since_days: int = 7, limit: int = 50) -> List[Task]:
        """
        Process new emails and extract tasks.
        
        Args:
            since_days: Number of days back to check for emails
            limit: Maximum number of emails to process in one batch
            
        Returns:
            List of extracted tasks
        """
        self.logger.info("Starting email processing")
        
        # Fetch new emails with limit
        new_emails = self.fetch_new_emails(since_days=since_days, limit=limit)
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
                    # DON'T mark as processed yet - let the main pipeline handle this
                    # after successful Notion creation
                else:
                    # If no task was extracted, mark as processed to avoid reprocessing
                    # non-task emails, but log it for debugging
                    self.processed_emails.add(email_msg.message_id)
                    self.logger.debug(f"Email marked as processed (no task found): {email_msg.subject}")
                
            except Exception as e:
                self.log_error(e, f"Processing email {email_msg.message_id}")
                # Don't mark as processed if there was an error - retry later
                continue
        
        # Save processed emails
        self._save_processed_emails()
        
        self.logger.info(f"Processed {len(new_emails)} emails, extracted {len(tasks)} tasks")
        return tasks
    
    def mark_task_as_processed(self, task: Task) -> None:
        """
        Mark a task's source email as processed.
        
        This should be called after successful task creation in external systems.
        
        Args:
            task: Task whose source email should be marked as processed
        """
        if task.source_id:
            self.processed_emails.add(task.source_id)
            self._save_processed_emails()
            self.logger.debug(f"Marked email as processed: {task.source_id}")
    
    def mark_tasks_as_processed(self, tasks: List[Task]) -> None:
        """
        Mark multiple tasks' source emails as processed.
        
        Args:
            tasks: List of tasks whose source emails should be marked as processed
        """
        for task in tasks:
            if task.source_id:
                self.processed_emails.add(task.source_id)
        
        self._save_processed_emails()
        self.logger.debug(f"Marked {len(tasks)} emails as processed")
    
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
