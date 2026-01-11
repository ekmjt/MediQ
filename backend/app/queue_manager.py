from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from app.models import QueueEntry, User
from app.triage_logic import get_severity_level

SEVERITY_WEIGHT = 0.7
WAIT_WEIGHT = 0.3
MAX_WAIT_THRESHOLD_MINUTES = 120  # 2 hours max wait normalization


class QueueManager:
    def __init__(self, db: Session):
        self.db = db

    def add_to_queue(self, user_id: int, severity_score: float) -> QueueEntry:
        """Add user to queue with calculated priority"""
        # Calculate initial priority score
        priority_score = self._calculate_priority_score(severity_score, 0)
        priority_level = get_severity_level(severity_score)
        
        # Create queue entry
        queue_entry = QueueEntry(
            user_id=user_id,
            severity_score=severity_score,
            priority_score=priority_score,
            priority_level=priority_level,
            position=0,  # Will be updated
            status="waiting"
        )
        
        self.db.add(queue_entry)
        self.db.commit()
        self.db.refresh(queue_entry)
        
        # Update all positions
        self.update_positions()
        
        return queue_entry

    def update_positions(self):
        """Recalculate all queue positions based on current priority scores"""
        # Update priority scores based on wait time
        queue_entries = self.db.query(QueueEntry).filter(
            QueueEntry.status == "waiting"
        ).all()
        
        current_time = datetime.utcnow()
        
        for entry in queue_entries:
            wait_time_minutes = (current_time - entry.created_at).total_seconds() / 60
            entry.wait_time_minutes = wait_time_minutes
            
            # Recalculate priority with updated wait time
            normalized_wait = min(wait_time_minutes / MAX_WAIT_THRESHOLD_MINUTES, 1.0)
            entry.priority_score = (
                SEVERITY_WEIGHT * entry.severity_score +
                WAIT_WEIGHT * (normalized_wait * 10)  # Scale to 1-10 range
            )
        
        self.db.commit()
        
        # Sort by priority score (descending) and assign positions
        sorted_entries = sorted(queue_entries, key=lambda x: x.priority_score, reverse=True)
        
        for position, entry in enumerate(sorted_entries, start=1):
            entry.position = position
        
        self.db.commit()

    def get_queue_position(self, user_id: int) -> Optional[int]:
        """Get current queue position for user"""
        entry = self.db.query(QueueEntry).filter(
            QueueEntry.user_id == user_id,
            QueueEntry.status == "waiting"
        ).first()
        
        if entry:
            self.update_positions()  # Ensure positions are current
            self.db.refresh(entry)
            return entry.position
        return None

    def get_queue_state(self) -> List[Dict]:
        """Get current queue state for all waiting users"""
        self.update_positions()
        
        entries = self.db.query(QueueEntry).filter(
            QueueEntry.status == "waiting"
        ).order_by(QueueEntry.position).all()
        
        return [
            {
                "queue_entry_id": entry.id,
                "user_id": entry.user_id,
                "position": entry.position,
                "severity_score": entry.severity_score,
                "priority_level": entry.priority_level,
                "wait_time_minutes": round(entry.wait_time_minutes, 1),
                "created_at": entry.created_at.isoformat()
            }
            for entry in entries
        ]

    def lower_position(self, user_id: int) -> bool:
        """User-initiated position lowering"""
        entry = self.db.query(QueueEntry).filter(
            QueueEntry.user_id == user_id,
            QueueEntry.status == "waiting"
        ).first()
        
        if not entry:
            return False
        
        # Reduce priority score by decreasing severity weight
        # This effectively moves them down in the queue
        entry.priority_score = entry.priority_score * 0.8  # Reduce by 20%
        self.db.commit()
        
        self.update_positions()
        return True

    def remove_from_queue(self, user_id: int) -> bool:
        """Remove user from queue"""
        entry = self.db.query(QueueEntry).filter(
            QueueEntry.user_id == user_id,
            QueueEntry.status == "waiting"
        ).first()
        
        if not entry:
            return False
        
        entry.status = "completed"
        self.db.commit()
        
        self.update_positions()
        return True

    def _calculate_priority_score(self, severity_score: float, wait_time_minutes: float) -> float:
        """Calculate priority score"""
        normalized_wait = min(wait_time_minutes / MAX_WAIT_THRESHOLD_MINUTES, 1.0)
        return (
            SEVERITY_WEIGHT * severity_score +
            WAIT_WEIGHT * (normalized_wait * 10)
        )

    def get_estimated_wait_time(self, position: int) -> int:
        """Estimate wait time in minutes based on position"""
        # Rough estimate: 15 minutes per position ahead
        return max(0, (position - 1) * 15)

