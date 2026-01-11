from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid
import json
from datetime import datetime

from app.models import Base, engine, SessionLocal, User, QueueEntry, ConversationHistory, CheckInLog, init_db
from app.gemini_service import GeminiService
from app.queue_manager import QueueManager
from app.triage_logic import is_emergency, get_care_recommendation
from app.scheduler import register_check_in_callback, unregister_check_in_callback, start_scheduler

# Initialize database
init_db()

app = FastAPI(title="MediQueue API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
gemini_service = GeminiService()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_personal_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

    async def broadcast_queue_update(self, queue_state: List[Dict]):
        """Broadcast queue updates to all connected clients"""
        message = {
            "type": "queue_update",
            "queue": queue_state
        }
        disconnected = []
        for session_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except:
                disconnected.append(session_id)
        
        for session_id in disconnected:
            self.disconnect(session_id)

manager = ConnectionManager()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic models
class StartTriageRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None


class MessageRequest(BaseModel):
    session_id: str
    content: str


class CompleteTriageRequest(BaseModel):
    session_id: str


class LowerPositionRequest(BaseModel):
    session_id: str


class CheckInResponseRequest(BaseModel):
    session_id: str
    queue_entry_id: int
    response: str  # "better", "same", "worse"


# HTTP Endpoints
@app.post("/api/start-triage")
async def start_triage(request: StartTriageRequest, db: Session = Depends(get_db)):
    """Begin triage conversation, create user session"""
    try:
        session_id = str(uuid.uuid4())
        
        user = User(
            session_id=session_id,
            name=request.name,
            phone=request.phone
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return {
            "session_id": session_id,
            "user_id": user.id,
            "message": "Welcome to MediQueue. I'm here to help assess your condition. How can I help you today?"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start triage: {str(e)}")


@app.post("/api/message")
async def send_message(request: MessageRequest, db: Session = Depends(get_db)):
    """Send message to Gemini and get response"""
    user = db.query(User).filter(User.session_id == request.session_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get conversation history
    history = db.query(ConversationHistory).filter(
        ConversationHistory.user_id == user.id
    ).order_by(ConversationHistory.timestamp.desc()).first()
    
    messages = []
    if history:
        messages = history.messages or []
    
    # Add new user message
    messages.append({"role": "user", "content": request.content})
    
    # Get user history for misuse detection
    user_history = {
        "misuse_count": user.misuse_count,
        "previous_severities": []
    }
    
    # Get AI response
    ai_response = gemini_service.get_conversation_response(messages, user_history)
    messages.append({"role": "assistant", "content": ai_response})
    
    # Save conversation history
    if history:
        history.messages = messages
        history.timestamp = datetime.utcnow()
    else:
        history = ConversationHistory(
            user_id=user.id,
            messages=messages,
            triage_result={}
        )
        db.add(history)
    
    db.commit()
    
    return {
        "response": ai_response,
        "messages": messages
    }


@app.post("/api/complete-triage")
async def complete_triage(request: CompleteTriageRequest, db: Session = Depends(get_db)):
    """Finalize triage, analyze conversation, add to queue"""
    user = db.query(User).filter(User.session_id == request.session_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get conversation history
    history = db.query(ConversationHistory).filter(
        ConversationHistory.user_id == user.id
    ).order_by(ConversationHistory.timestamp.desc()).first()
    
    if not history or not history.messages:
        raise HTTPException(status_code=400, detail="No conversation found")
    
    # Get previous severities for misuse detection
    previous_entries = db.query(QueueEntry).filter(
        QueueEntry.user_id == user.id,
        QueueEntry.status != "waiting"  # Get completed/cancelled entries
    ).all()
    previous_severities = [float(entry.severity_score) for entry in previous_entries]
    
    # Analyze triage
    user_history = {
        "misuse_count": user.misuse_count,
        "previous_severities": previous_severities
    }
    
    triage_result = gemini_service.analyze_triage(history.messages, user_history)
    
    # Check for misuse
    misuse_check = gemini_service.check_misuse(
        triage_result["severity_score"],
        user_history
    )
    
    if misuse_check["is_misuse"]:
        user.misuse_count += 1
        db.commit()
    
    # Update history with triage result
    history.triage_result = triage_result
    db.commit()
    
    # Add to queue
    queue_manager = QueueManager(db)
    queue_entry = queue_manager.add_to_queue(user.id, triage_result["severity_score"])
    
    # Check if emergency
    emergency = is_emergency(
        triage_result.get("symptoms_summary", ""),
        triage_result["severity_score"]
    )
    
    # Broadcast queue update
    queue_state = queue_manager.get_queue_state()
    await manager.broadcast_queue_update(queue_state)
    
    # Register for check-ins
    async def check_in_callback(message: dict):
        await manager.send_personal_message(message, request.session_id)
    
    register_check_in_callback(request.session_id, check_in_callback)
    
    return {
        "triage_result": triage_result,
        "queue_position": queue_entry.position,
        "emergency": emergency,
        "care_recommendation": get_care_recommendation(queue_entry.priority_level),
        "misuse_warning": misuse_check["reason"] if misuse_check["is_misuse"] else None
    }


@app.get("/api/queue")
async def get_queue(db: Session = Depends(get_db)):
    """Get current queue state"""
    queue_manager = QueueManager(db)
    return {"queue": queue_manager.get_queue_state()}


@app.post("/api/lower-position")
async def lower_position(request: LowerPositionRequest, db: Session = Depends(get_db)):
    """User-initiated position lowering"""
    user = db.query(User).filter(User.session_id == request.session_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    queue_manager = QueueManager(db)
    success = queue_manager.lower_position(user.id)
    
    if success:
        queue_state = queue_manager.get_queue_state()
        await manager.broadcast_queue_update(queue_state)
        return {"message": "Position lowered successfully", "queue": queue_state}
    else:
        raise HTTPException(status_code=400, detail="Could not lower position")


@app.post("/api/check-in-response")
async def check_in_response(request: CheckInResponseRequest, db: Session = Depends(get_db)):
    """Respond to periodic check-in"""
    user = db.query(User).filter(User.session_id == request.session_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    queue_entry = db.query(QueueEntry).filter(
        QueueEntry.id == request.queue_entry_id,
        QueueEntry.user_id == user.id
    ).first()
    
    if not queue_entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    
    # Log check-in response
    check_in_log = CheckInLog(
        user_id=user.id,
        queue_entry_id=queue_entry.id,
        response=request.response
    )
    db.add(check_in_log)
    
    queue_entry.last_check_in = datetime.utcnow()
    
    # If condition worsened, increase severity
    if request.response == "worse":
        queue_entry.severity_score = min(10, queue_entry.severity_score + 1)
        queue_manager = QueueManager(db)
        queue_manager.update_positions()
        queue_state = queue_manager.get_queue_state()
        await manager.broadcast_queue_update(queue_state)
    
    db.commit()
    
    return {"message": "Check-in response recorded", "response": request.response}


# WebSocket endpoint
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WebSocket messages if needed
            # For now, just keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        unregister_check_in_callback(session_id)


@app.on_event("startup")
async def startup_event():
    """Initialize scheduler on startup"""
    start_scheduler()


@app.on_event("shutdown")
async def shutdown_event():
    """Stop scheduler on shutdown"""
    from app.scheduler import scheduler
    if scheduler.running:
        scheduler.shutdown()


@app.get("/")
async def root():
    return {"message": "MediQueue API", "status": "running"}


@app.get("/api/model-info")
async def get_model_info():
    """Get information about the Gemini model being used"""
    return {
        "model_name": gemini_service.model_name,
        "status": "active"
    }

