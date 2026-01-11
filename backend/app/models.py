from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Get the backend directory (parent of app directory)
# Use __file__ to get the absolute path of this module
current_file_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_file_dir)
db_path = os.path.join(backend_dir, "database.db")

# Ensure the directory exists
os.makedirs(backend_dir, exist_ok=True)

# Use absolute path for SQLite database
# Always use absolute path to avoid issues with relative paths from .env
db_path_absolute = os.path.abspath(db_path)
# SQLAlchemy SQLite format: sqlite:////absolute/path (4 slashes for absolute paths)
# Always use the computed absolute path, ignoring DATABASE_URL from .env if it's relative
DATABASE_URL = f"sqlite:///{db_path_absolute}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    misuse_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    queue_entries = relationship("QueueEntry", back_populates="user")
    conversation_histories = relationship("ConversationHistory", back_populates="user")
    check_in_logs = relationship("CheckInLog", back_populates="user")


class QueueEntry(Base):
    __tablename__ = "queue_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    severity_score = Column(Float)
    priority_score = Column(Float)
    priority_level = Column(String)  # Critical, High, Medium, Low
    wait_time_minutes = Column(Float, default=0)
    position = Column(Integer)
    status = Column(String, default="waiting")  # waiting, in_progress, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    last_check_in = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="queue_entries")
    check_in_logs = relationship("CheckInLog", back_populates="queue_entry")


class ConversationHistory(Base):
    __tablename__ = "conversation_histories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    messages = Column(JSON)  # List of message objects
    triage_result = Column(JSON)  # {severity, guidance, emergency_flag}
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="conversation_histories")


class CheckInLog(Base):
    __tablename__ = "check_in_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    queue_entry_id = Column(Integer, ForeignKey("queue_entries.id"))
    response = Column(String)  # better, same, worse
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="check_in_logs")
    queue_entry = relationship("QueueEntry", back_populates="check_in_logs")


def init_db():
    Base.metadata.create_all(bind=engine)

