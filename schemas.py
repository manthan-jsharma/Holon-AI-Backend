from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ActionItem(BaseModel):
    text: str
    assignee: Optional[str] = None
    due_date: Optional[str] = None

class Decision(BaseModel):
    text: str

class Participant(BaseModel):
    name: str
    speaking_time: Optional[str] = None

class MeetingBase(BaseModel):
    title: str
    language: str

class MeetingCreate(MeetingBase):
    id: int
    status: str

class Meeting(MeetingBase):
    id: int
    date: str
    status: str
    duration: Optional[str] = None
    
    class Config:
        orm_mode = True

class MeetingDetail(Meeting):
    transcript: Optional[str] = None
    summary: Optional[str] = None
    action_items: Optional[List[Dict[str, Any]]] = None
    decisions: Optional[List[Dict[str, Any]]] = None
    participants: Optional[List[Dict[str, Any]]] = None
    error_message: Optional[str] = None
    
    class Config:
        orm_mode = True
