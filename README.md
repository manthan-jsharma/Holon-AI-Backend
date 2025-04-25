# Multilingual Meeting Assistant Backend

This is the FastAPI backend for the Multilingual Meeting Assistant application.

## Features

- Audio transcription using Alibaba Cloud ASR
- Meeting summarization using LangChain with Qwen/DeepSeek
- PDF generation of meeting notes
- RESTful API for CRUD operations

## Setup

### Prerequisites

- Python 3.8 or higher
- Alibaba Cloud account with ASR service enabled
- API keys for Alibaba Cloud

### Environment Variables

Create a `.env` file in the root directory with the following variables:

\`\`\`
ALIBABA_ACCESS_KEY_ID=your_access_key_id
ALIBABA_ACCESS_KEY_SECRET=your_access_key_secret
ALIBABA_APP_KEY=your_app_key
\`\`\`

### Installation

1. Clone the repository
2. Create a virtual environment:
   \`\`\`
   python -m venv venv
   \`\`\`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`
5. Run the server:
   \`\`\`
   uvicorn main:app --reload
   \`\`\`

The API will be available at http://localhost:8000

## API Endpoints

- `POST /meetings/`: Upload a new meeting recording
- `GET /meetings/`: Get all meetings
- `GET /meetings/{meeting_id}`: Get a specific meeting
- `DELETE /meetings/{meeting_id}`: Delete a meeting
- `POST /meetings/{meeting_id}/export`: Export meeting as PDF
- `GET /meetings/{meeting_id}/search`: Search within a meeting

## Directory Structure

- `main.py`: FastAPI application
- `database.py`: Database configuration
- `models.py`: SQLAlchemy models
- `schemas.py`: Pydantic schemas
- `services/`: Service modules
  - `transcription_service.py`: Alibaba ASR integration
  - `summarization_service.py`: LangChain integration
  - `pdf_service.py`: PDF generation
- `uploads/`: Directory for uploaded audio files
- `pdfs/`: Directory for generated PDFs
