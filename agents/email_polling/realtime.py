"""
Real-time email processing with IMAP IDLE and webhook support.

This module provides immediate email processing through:
1. IMAP IDLE - Real-time push notifications from email server
2. Webhook endpoint - For email services that support webhooks
3. Fallback polling - Continue regular polling for resilience
"""

import asyncio
import threading
import time
from typing import Callable, Optional, Dict, Any
from loguru import logger
from imapclient import IMAPClient
from imapclient.exceptions import IMAPClientError
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta

from config.settings import settings


class RealTimeEmailProcessor:
    """
    Real-time email processor with IMAP IDLE and webhook support.
    
    This class provides immediate email processing while maintaining
    fallback polling for resilience.
    """
    
    def __init__(self, email_callback: Callable):
        """
        Initialize the real-time email processor.
        
        Args:
            email_callback: Function to call when new emails are detected
        """
        self.logger = logger.bind(component="realtime_email")
        self.email_callback = email_callback
        self.idle_thread = None
        self.idle_running = False
        self.last_idle_restart = datetime.now()
        self.idle_restart_interval = 1800  # Restart IDLE every 30 minutes
        
        # Connection settings
        self.imap_server = settings.email_imap_server
        self.imap_port = settings.email_imap_port
        self.email_address = settings.email_address
        self.email_password = settings.email_password
        
        self.logger.info("Real-time email processor initialized")
    
    def start_idle_monitoring(self) -> None:
        """Start IMAP IDLE monitoring in a separate thread."""
        if self.idle_thread and self.idle_thread.is_alive():
            self.logger.warning("IDLE monitoring already running")
            return
        
        self.idle_running = True
        self.idle_thread = threading.Thread(target=self._idle_monitor_loop, daemon=True)
        self.idle_thread.start()
        self.logger.info("Started IMAP IDLE monitoring")
    
    def stop_idle_monitoring(self) -> None:
        """Stop IMAP IDLE monitoring."""
        self.idle_running = False
        if self.idle_thread:
            self.idle_thread.join(timeout=10)
        self.logger.info("Stopped IMAP IDLE monitoring")
    
    def _idle_monitor_loop(self) -> None:
        """Main IDLE monitoring loop."""
        while self.idle_running:
            try:
                self._run_idle_session()
            except Exception as e:
                self.logger.error(f"IDLE session error: {e}")
                if self.idle_running:
                    time.sleep(30)  # Wait before retrying
    
    def _run_idle_session(self) -> None:
        """Run a single IDLE session."""
        client = None
        try:
            # Connect to IMAP server
            client = IMAPClient(self.imap_server, port=self.imap_port, use_uid=True, ssl=True)
            client.login(self.email_address, self.email_password)
            client.select_folder('INBOX')
            
            session_start = datetime.now()
            self.logger.info("Started IDLE session")
            
            # Start IDLE
            client.idle()
            
            while self.idle_running:
                # Check for new messages
                try:
                    responses = client.idle_check(timeout=60)  # Check every minute
                    
                    if responses:
                        # New messages detected
                        self.logger.info(f"IDLE: New messages detected: {len(responses)}")
                        
                        # Exit IDLE to process messages
                        client.idle_done()
                        
                        # Trigger email processing
                        self._trigger_email_processing()
                        
                        # Restart IDLE
                        client.idle()
                        
                    # Restart IDLE session periodically (server timeout prevention)
                    if datetime.now() - session_start > timedelta(seconds=self.idle_restart_interval):
                        self.logger.info("Restarting IDLE session")
                        client.idle_done()
                        break
                        
                except IMAPClientError as e:
                    self.logger.error(f"IDLE check error: {e}")
                    break
                    
            # Clean up IDLE
            try:
                client.idle_done()
            except:
                pass
                
        except Exception as e:
            self.logger.error(f"IDLE session setup error: {e}")
            
        finally:
            if client:
                try:
                    client.logout()
                except:
                    pass
    
    def _trigger_email_processing(self) -> None:
        """Trigger email processing callback."""
        try:
            self.logger.info("Triggering real-time email processing")
            
            # Run the callback in a separate thread to avoid blocking IDLE
            processing_thread = threading.Thread(
                target=self._run_email_callback,
                daemon=True
            )
            processing_thread.start()
            
        except Exception as e:
            self.logger.error(f"Error triggering email processing: {e}")
    
    def _run_email_callback(self) -> None:
        """Run the email callback in a separate thread."""
        try:
            # Use asyncio to run the callback if it's async
            if asyncio.iscoroutinefunction(self.email_callback):
                asyncio.run(self.email_callback())
            else:
                self.email_callback()
                
        except Exception as e:
            self.logger.error(f"Email callback error: {e}")
    
    def process_webhook_notification(self, webhook_data: Dict[str, Any]) -> None:
        """
        Process webhook notification from email service.
        
        Args:
            webhook_data: Webhook payload data
        """
        self.logger.info(f"Processing webhook notification: {webhook_data}")
        
        try:
            # Extract relevant information from webhook
            # This would vary based on the email service provider
            
            # Trigger email processing
            self._trigger_email_processing()
            
        except Exception as e:
            self.logger.error(f"Webhook processing error: {e}")
    
    def is_idle_supported(self) -> bool:
        """
        Check if the email server supports IMAP IDLE.
        
        Returns:
            bool: True if IDLE is supported
        """
        try:
            client = IMAPClient(self.imap_server, port=self.imap_port, use_uid=True, ssl=True)
            client.login(self.email_address, self.email_password)
            
            # Check if IDLE capability is available
            capabilities = client.capabilities()
            idle_supported = b'IDLE' in capabilities
            
            client.logout()
            
            self.logger.info(f"IMAP IDLE supported: {idle_supported}")
            return idle_supported
            
        except Exception as e:
            self.logger.error(f"Error checking IDLE support: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of real-time processing.
        
        Returns:
            Dict[str, Any]: Status information
        """
        return {
            "idle_running": self.idle_running,
            "idle_thread_alive": self.idle_thread.is_alive() if self.idle_thread else False,
            "last_idle_restart": self.last_idle_restart.isoformat(),
            "idle_supported": self.is_idle_supported(),
            "restart_interval": self.idle_restart_interval
        }
