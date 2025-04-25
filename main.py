from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from datetime import datetime

from database import get_db, engine, Base
import models
import schemas
from services.transcription_service import transcribe_audio
from services.summarization_service import generate_summary
from services.pdf_service import generate_pdf

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Multilingual Meeting Assistant API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("pdfs", exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Multilingual Meeting Assistant API"}

@app.post("/meetings/", response_model=schemas.MeetingCreate)
async def create_meeting(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    primary_language: str = Form(...),
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Generate unique filename
    file_extension = os.path.splitext(audio_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = f"uploads/{unique_filename}"
    
    # Save uploaded file
    with open(file_path, "wb") as buffer:
        buffer.write(await audio_file.read())
    
    # Create meeting record
    meeting = models.Meeting(
        title=title,
        date=datetime.now().strftime("%Y-%m-%d"),
        language=primary_language,
        audio_path=file_path,
        status="processing"
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    
    # Process audio in background
    background_tasks.add_task(
        process_meeting, 
        meeting_id=meeting.id, 
        file_path=file_path, 
        language=primary_language
    )
    
    return {"id": meeting.id, "title": title, "status": "processing"}

async def process_meeting(meeting_id: int, file_path: str, language: str):
    db = next(get_db())
    try:
        # Get meeting
        meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
        if not meeting:
            return
        
        # Transcribe audio using Alibaba ASR
        transcript = await transcribe_audio(file_path, language)
        
        # Generate summary using LangChain with Qwen/DeepSeek
        summary_data = await generate_summary(transcript, language)
        
        # Update meeting with results
        meeting.transcript = transcript
        meeting.summary = summary_data["summary"]
        meeting.action_items = summary_data["action_items"]
        meeting.decisions = summary_data["decisions"]
        meeting.status = "completed"
        meeting.duration = summary_data.get("duration", "Unknown")
        meeting.participants = summary_data.get("participants", [])
        
        db.commit()
    except Exception as e:
        # Update meeting status to failed
        meeting.status = "failed"
        meeting.error_message = str(e)
        db.commit()
        raise e
    finally:
        db.close()

@app.get("/meetings/", response_model=List[schemas.Meeting])
def get_meetings(db: Session = Depends(get_db)):
    meetings = db.query(models.Meeting).order_by(models.Meeting.date.desc()).all()
    return meetings

@app.get("/meetings/{meeting_id}", response_model=schemas.MeetingDetail)
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@app.delete("/meetings/{meeting_id}")
def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Delete associated files
    if meeting.audio_path and os.path.exists(meeting.audio_path):
        os.remove(meeting.audio_path)
    
    # Delete PDF if exists
    pdf_path = f"pdfs/meeting_{meeting_id}.pdf"
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    
    # Delete from database
    db.delete(meeting)
    db.commit()
    
    return {"message": "Meeting deleted successfully"}

@app.post("/meetings/{meeting_id}/export")
def export_meeting_as_pdf(meeting_id: int, db: Session = Depends(get_db)):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if meeting.status != "completed":
        raise HTTPException(status_code=400, detail="Meeting processing not completed")
    
    # Generate PDF
    pdf_path = f"pdfs/meeting_{meeting_id}.pdf"
    generate_pdf(meeting, pdf_path)
    
    return FileResponse(
        path=pdf_path,
        filename=f"{meeting.title.replace(' ', '_')}_notes.pdf",
        media_type="application/pdf"
    )

@app.get("/meetings/{meeting_id}/search")
def search_in_meeting(meeting_id: int, query: str, db: Session = Depends(get_db)):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if meeting.status != "completed":
        raise HTTPException(status_code=400, detail="Meeting processing not completed")
    
    # Search in transcript
    transcript_matches = []
    if meeting.transcript:
        transcript_lines = meeting.transcript.split("\n")
        transcript_matches = [line for line in transcript_lines if query.lower() in line.lower()]
    
    # Search in summary
    summary_match = None
    if meeting.summary and query.lower() in meeting.summary.lower():
        summary_match = meeting.summary
    
    # Search in action items
    action_item_matches = []
    if meeting.action_items:
        action_item_matches = [item for item in meeting.action_items if query.lower() in item["text"].lower()]
    
    # Search in decisions
    decision_matches = []
    if meeting.decisions:
        decision_matches = [decision for decision in meeting.decisions if query.lower() in decision["text"].lower()]
    
    return {
        "transcript_matches": transcript_matches,
        "summary_match": summary_match,
        "action_item_matches": action_item_matches,
        "decision_matches": decision_matches
    }
