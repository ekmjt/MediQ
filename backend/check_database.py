#!/usr/bin/env python3
"""
Script to check database contents
Run this from the backend directory: python check_database.py
"""

import sys
import os
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.models import SessionLocal, User, QueueEntry, ConversationHistory, CheckInLog

def format_datetime(dt):
    """Format datetime for display"""
    if dt:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return "None"

def print_users(db):
    """Print all users"""
    users = db.query(User).all()
    print("\n" + "="*80)
    print("USERS TABLE")
    print("="*80)
    if not users:
        print("No users found in database.")
        return
    
    for user in users:
        print(f"\nUser ID: {user.id}")
        print(f"  Session ID: {user.session_id}")
        print(f"  Name: {user.name or 'Not provided'}")
        print(f"  Phone: {user.phone or 'Not provided'}")
        print(f"  Misuse Count: {user.misuse_count}")
        print(f"  Created At: {format_datetime(user.created_at)}")
        print(f"  Queue Entries: {len(user.queue_entries)}")
        print(f"  Conversation Histories: {len(user.conversation_histories)}")
        print(f"  Check-in Logs: {len(user.check_in_logs)}")

def print_queue_entries(db):
    """Print all queue entries"""
    entries = db.query(QueueEntry).order_by(QueueEntry.created_at.desc()).all()
    print("\n" + "="*80)
    print("QUEUE ENTRIES TABLE")
    print("="*80)
    if not entries:
        print("No queue entries found in database.")
        return
    
    for entry in entries:
        print(f"\nQueue Entry ID: {entry.id}")
        print(f"  User ID: {entry.user_id}")
        if entry.user:
            print(f"  User Session ID: {entry.user.session_id}")
            print(f"  User Name: {entry.user.name or 'Not provided'}")
        print(f"  Severity Score: {entry.severity_score}")
        print(f"  Priority Score: {entry.priority_score}")
        print(f"  Priority Level: {entry.priority_level}")
        print(f"  Position: {entry.position}")
        print(f"  Status: {entry.status}")
        print(f"  Wait Time (minutes): {entry.wait_time_minutes}")
        print(f"  Created At: {format_datetime(entry.created_at)}")
        print(f"  Last Check-in: {format_datetime(entry.last_check_in)}")

def print_conversation_histories(db):
    """Print all conversation histories"""
    histories = db.query(ConversationHistory).order_by(ConversationHistory.timestamp.desc()).all()
    print("\n" + "="*80)
    print("CONVERSATION HISTORIES TABLE")
    print("="*80)
    if not histories:
        print("No conversation histories found in database.")
        return
    
    for history in histories:
        print(f"\nConversation History ID: {history.id}")
        print(f"  User ID: {history.user_id}")
        if history.user:
            print(f"  User Session ID: {history.user.session_id}")
            print(f"  User Name: {history.user.name or 'Not provided'}")
        print(f"  Timestamp: {format_datetime(history.timestamp)}")
        print(f"  Number of Messages: {len(history.messages) if history.messages else 0}")
        
        if history.messages:
            print(f"  Messages:")
            for i, msg in enumerate(history.messages[:3], 1):  # Show first 3 messages
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:100]  # First 100 chars
                print(f"    {i}. [{role}]: {content}...")
            if len(history.messages) > 3:
                print(f"    ... and {len(history.messages) - 3} more messages")
        
        if history.triage_result:
            print(f"  Triage Result:")
            print(f"    Severity Score: {history.triage_result.get('severity_score', 'N/A')}")
            print(f"    Emergency Flag: {history.triage_result.get('emergency_flag', 'N/A')}")
            if 'guidance' in history.triage_result:
                guidance = history.triage_result['guidance'][:100]
                print(f"    Guidance: {guidance}...")

def print_check_in_logs(db):
    """Print all check-in logs"""
    logs = db.query(CheckInLog).order_by(CheckInLog.timestamp.desc()).all()
    print("\n" + "="*80)
    print("CHECK-IN LOGS TABLE")
    print("="*80)
    if not logs:
        print("No check-in logs found in database.")
        return
    
    for log in logs:
        print(f"\nCheck-in Log ID: {log.id}")
        print(f"  User ID: {log.user_id}")
        if log.user:
            print(f"  User Session ID: {log.user.session_id}")
        print(f"  Queue Entry ID: {log.queue_entry_id}")
        print(f"  Response: {log.response}")
        print(f"  Timestamp: {format_datetime(log.timestamp)}")

def print_summary(db):
    """Print summary statistics"""
    print("\n" + "="*80)
    print("DATABASE SUMMARY")
    print("="*80)
    
    user_count = db.query(User).count()
    queue_count = db.query(QueueEntry).count()
    history_count = db.query(ConversationHistory).count()
    log_count = db.query(CheckInLog).count()
    
    waiting_count = db.query(QueueEntry).filter(QueueEntry.status == "waiting").count()
    in_progress_count = db.query(QueueEntry).filter(QueueEntry.status == "in_progress").count()
    completed_count = db.query(QueueEntry).filter(QueueEntry.status == "completed").count()
    
    print(f"\nTotal Users: {user_count}")
    print(f"Total Queue Entries: {queue_count}")
    print(f"  - Waiting: {waiting_count}")
    print(f"  - In Progress: {in_progress_count}")
    print(f"  - Completed: {completed_count}")
    print(f"Total Conversation Histories: {history_count}")
    print(f"Total Check-in Logs: {log_count}")

def main():
    db = SessionLocal()
    try:
        print_summary(db)
        print_users(db)
        print_queue_entries(db)
        print_conversation_histories(db)
        print_check_in_logs(db)
        print("\n" + "="*80)
        print("END OF REPORT")
        print("="*80 + "\n")
    finally:
        db.close()

if __name__ == "__main__":
    main()

