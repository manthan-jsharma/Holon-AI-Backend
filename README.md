
# I have totally changed the code to Use the Whisper-ffmpeg method and Langchain-Qwen-HuggingFace Pipeline Method for Indian Users, So just Clone the Repository and Get Guide From ALternative Method written below.

# Multilingual Meeting Assistant Backend

This is the FastAPI backend for the Multilingual Meeting Assistant application.

## Features

- Audio transcription using Alibaba Cloud ASR, Alternative Whisper-FFmpeg.
- Meeting summarization using LangChain with Qwen/DeepSeek with HuggingFace-Pipeline and transformers.
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

The API will be available at http://localhost:8000/docs

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


## Alternate Method
- For indian users, both the QWEN and Langchain wont be working without the access to Alibaba Console, which is not available in india.
- To tackle tht=at issue Follow this Provided Steps:
1. Install Dependencies
- pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118  # for CUDA 11.8
- pip install git+https://github.com/openai/whisper.git
- pip install transformers accelerate
- pip install langchain huggingface_hub
- pip install ffmpeg-python

 2. Install FFmpeg (System Level)
Whisper depends on FFmpeg to decode audio.

✅ For Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg
✅ For macOS (via Homebrew): brew install ffmpeg


3. This is basically an alternative setup without API keys needed.

4. For Deployment Look for  Render, Railway, Fly.io, or a VPS (like DigitalOcean).



## Deployment Tips

1.Use a Dockerfile:

This ensures your server has Python, ffmpeg, and Whisper installed.

You have full control over dependencies.

2.Install ffmpeg system-wide in the Docker image:

Whisper needs access to the ffmpeg binary in the system path.

Example: apt install ffmpeg (for Debian/Ubuntu-based images).

3.Install Whisper in requirements.txt:

Include openai-whisper, torch, ffmpeg-python etc.

4.Test locally inside Docker before deploying.
