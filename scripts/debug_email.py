#!/usr/bin/env python3
"""
Debug script to test email processing functionality.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from agents.main import AgentOrchestrator
from agents.email_polling import EmailAgent
from config.settings import settings

async def debug_email_processing():
    """Debug email processing step by step."""
    print("🔍 Debugging Email Processing")
    print("=" * 50)
    
    # Step 1: Check configuration
    print("\n1. Checking configuration...")
    print(f"   Email Address: {settings.email_address}")
    print(f"   IMAP Server: {settings.email_imap_server}")
    print(f"   IMAP Port: {settings.email_imap_port}")
    print(f"   Email Password: {'*' * len(settings.email_password) if settings.email_password else 'NOT SET'}")
    
    # Step 2: Test email connection
    print("\n2. Testing email connection...")
    try:
        email_agent = EmailAgent()
        mail = email_agent.connect_to_email()
        print("   ✅ Email connection successful")
        
        # Check inbox status
        status, num_messages = mail.select('inbox')
        print(f"   📧 Inbox status: {status}")
        print(f"   📧 Total messages: {num_messages[0].decode()}")
        
        # Check for recent emails
        from datetime import datetime, timedelta
        since_date = (datetime.now() - timedelta(days=1)).strftime('%d-%b-%Y')
        search_criteria = f'(SINCE {since_date})'
        print(f"   🔍 Searching for emails since: {since_date}")
        
        status, messages = mail.search(None, search_criteria)
        email_ids = messages[0].split()
        print(f"   📧 Found {len(email_ids)} emails in last 24 hours")
        
        # Check for unread emails
        status, unread_messages = mail.search(None, '(UNSEEN)')
        unread_ids = unread_messages[0].split()
        print(f"   📧 Found {len(unread_ids)} unread emails")
        
        # Show details of the last email
        if email_ids:
            latest_id = email_ids[-1]
            print(f"\n   📧 Latest email details (ID: {latest_id.decode()}):")
            
            status, msg_data = mail.fetch(latest_id, '(RFC822)')
            if status == 'OK':
                import email
                email_message = email.message_from_bytes(msg_data[0][1])
                
                subject = email_message.get('Subject', '')
                sender = email_message.get('From', '')
                date_str = email_message.get('Date', '')
                
                print(f"      Subject: {subject}")
                print(f"      From: {sender}")
                print(f"      Date: {date_str}")
                
                # Extract content
                content = ""
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            payload = part.get_payload(decode=True)
                            if payload:
                                content = payload.decode('utf-8', errors='ignore')
                                break
                else:
                    payload = email_message.get_payload(decode=True)
                    if payload:
                        content = payload.decode('utf-8', errors='ignore')
                
                print(f"      Content preview: {content[:200]}...")
        
        mail.close()
        
    except Exception as e:
        print(f"   ❌ Email connection failed: {e}")
        return False
    
    # Step 3: Test email processing
    print("\n3. Testing email processing...")
    try:
        email_agent = EmailAgent()
        new_emails = email_agent.fetch_new_emails()
        print(f"   📧 Fetched {len(new_emails)} new emails")
        
        for i, email_msg in enumerate(new_emails):
            print(f"   📧 Email {i+1}:")
            print(f"      Subject: {email_msg.subject}")
            print(f"      From: {email_msg.sender}")
            print(f"      Date: {email_msg.date}")
            print(f"      Content length: {len(email_msg.content)} chars")
            
            # Test task extraction
            print(f"      Testing task extraction...")
            task = await email_agent.extract_tasks_from_email(email_msg)
            if task:
                print(f"      ✅ Task extracted: {task.title}")
                print(f"      Priority: {task.priority}")
                print(f"      Description: {task.description}")
            else:
                print(f"      ❌ No task extracted")
    
    except Exception as e:
        print(f"   ❌ Email processing failed: {e}")
        return False
    
    # Step 4: Test full pipeline
    print("\n4. Testing full pipeline...")
    try:
        orchestrator = AgentOrchestrator()
        await orchestrator.run_single_cycle()
        
        stats = orchestrator.get_system_stats()
        print(f"   📊 Pipeline stats:")
        print(f"      Tasks processed: {stats['tasks_processed']}")
        print(f"      Emails processed: {stats['emails_processed']}")
        print(f"      Errors: {stats['errors']}")
        
    except Exception as e:
        print(f"   ❌ Pipeline failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(debug_email_processing())
    
    if success:
        print("\n🎉 Debug completed successfully!")
    else:
        print("\n❌ Debug failed!")
