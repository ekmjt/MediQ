from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import QueueEntry, CheckInLog
from app.queue_manager import QueueManager
from typing import Dict, Callable
import asyncio

scheduler = AsyncIOScheduler()
check_in_callbacks: Dict[str, Callable] = {}  # session_id -> callback function


def register_check_in_callback(session_id: str, callback: Callable):
    """Register a callback function for check-ins"""
    check_in_callbacks[session_id] = callback


def unregister_check_in_callback(session_id: str):
    """Unregister a callback function"""
    if session_id in check_in_callbacks:
        del check_in_callbacks[session_id]


async def periodic_check_in_task(db: Session):
    """Check in with users every 30 minutes"""
    current_time = datetime.utcnow()
    check_in_interval = timedelta(minutes=30)
    
    # Get all active queue entries
    queue_entries = db.query(QueueEntry).filter(
        QueueEntry.status == "waiting"
    ).all()
    
    for entry in queue_entries:
        # Check if it's time for a check-in
        last_check_in = entry.last_check_in or entry.created_at
        time_since_check_in = current_time - last_check_in
        
        if time_since_check_in >= check_in_interval:
            # Send check-in notification via WebSocket
            user = entry.user
            if user and user.session_id in check_in_callbacks:
                callback = check_in_callbacks[user.session_id]
                try:
                    await callback({
                        "type": "check_in",
                        "user_id": user.id,
                        "queue_entry_id": entry.id,
                        "message": "How are you feeling? Please let us know if your condition has changed."
                    })
                    # Update last check-in time
                    entry.last_check_in = current_time
                    db.commit()
                except Exception as e:
                    print(f"Error sending check-in to {user.session_id}: {e}")


def start_scheduler():
    """Start the periodic check-in scheduler"""
    from app.models import SessionLocal
    if not scheduler.running:
        async def job_wrapper():
            db = SessionLocal()
            try:
                await periodic_check_in_task(db)
            finally:
                db.close()
        
        scheduler.add_job(
            job_wrapper,
            IntervalTrigger(minutes=30),
            id="periodic_check_in",
            replace_existing=True
        )
        scheduler.start()
        print("Scheduler started - periodic check-ins every 30 minutes")


def stop_scheduler():
    """Stop the scheduler"""
    if scheduler.running:
        scheduler.shutdown()

