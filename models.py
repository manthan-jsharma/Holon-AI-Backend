from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from database import Base

class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    date = Column(String)
    language = Column(String)
    audio_path = Column(String)
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    action_items = Column(JSON, nullable=True)
    decisions = Column(JSON, nullable=True)
    participants = Column(JSON, nullable=True)
    duration = Column(String, nullable=True)
    status = Column(String)  # processing, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
