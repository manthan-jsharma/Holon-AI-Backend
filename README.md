# 🎙️ Multilingual Meeting Assistant Backend

This is a robust **FastAPI-based** backend designed to power the Multilingual Meeting Assistant. It streamlines the lifecycle of meeting documentation—from raw audio ingestion and high-accuracy transcription to intelligent summarization and professional PDF report generation.

The system now supports a **hybrid architecture**, offering both cloud-based processing via Alibaba Cloud and a fully local, open-source pipeline (Whisper + HuggingFace) for **INDIAN** users without cloud console access.

---

## ✨ Key Features

* **Dual Transcription Engine**: Supports **Alibaba Cloud ASR** for enterprise-grade speed or a local **Whisper-FFmpeg** implementation for privacy and cost-efficiency.
* **Intelligent Summarization**: Leverages **LangChain** integrated with **Qwen/DeepSeek** models via HuggingFace pipelines to extract action items and key takeaways.
* **Professional Documentation**: Automated generation of meeting notes in **PDF format**.
* **Comprehensive API**: RESTful endpoints for meeting management (CRUD), advanced search within transcripts, and file exports.

---

## 🛠️ Tech Stack

| Component | Technology |
| --- | --- |
| **Framework** | FastAPI (Python 3.8+) |
| **ORM/Database** | SQLAlchemy, SQLite/PostgreSQL |
| **AI/ML (Cloud)** | Alibaba Cloud ASR, Qwen LLM |
| **AI/ML (Local)** | OpenAI Whisper, HuggingFace Transformers |
| **Orchestration** | LangChain |
| **Processing** | FFmpeg (Audio), Pydantic (Validation) |

---

## 🚀 Getting Started

### 📋 Prerequisites

* Python 3.8 or higher.
* **Optional**: Alibaba Cloud account with ASR enabled (if using the cloud method).
* **System Level**: FFmpeg installed on your machine.

### 📥 Installation

1. **Clone the Repository**
```bash
git clone https://github.com/your-username/meeting-assistant-backend.git
cd meeting-assistant-backend

```


2. **Environment Setup**
Create a virtual environment and activate it:
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

```


3. **Install Dependencies**
```bash
pip install -r requirements.txt

```


4. **Configuration**
Create a `.env` file in the root directory:
```env
ALIBABA_ACCESS_KEY_ID=your_id
ALIBABA_ACCESS_KEY_SECRET=your_secret
ALIBABA_APP_KEY=your_app_key

```


5. **Run the Application**
```bash
uvicorn main:app --reload

```


Access the interactive API docs at: `http://localhost:8000/docs`

---

## 🌍 Alternative Method (Local/No API Keys)

For users unable to access the Alibaba Cloud Console (including users in specific regions like India), follow this setup to run the **Whisper-FFmpeg** and **HuggingFace Pipeline**. This method runs entirely on your local hardware.

### 1. Install GPU-Accelerated PyTorch (Recommended)

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

```

### 2. Install AI Libraries

```bash
pip install git+https://github.com/openai/whisper.git
pip install transformers accelerate langchain huggingface_hub ffmpeg-python einops==0.7.0

```

### 3. Model Selection

By default, the system is configured to use **Qwen1.5-0.5B** (~1GB) for summarization, which offers a great balance between performance and resource usage. You may also opt for the smaller **Qwen-2** models.

---

## 📂 Directory Structure

```text
├── main.py                # Application entry point
├── database.py            # Database connection logic
├── models.py              # SQLAlchemy database models
├── schemas.py             # Pydantic data schemas
├── services/              # Core business logic
│   ├── transcription.py   # Alibaba & Whisper integration
│   ├── summarization.py   # LangChain & HuggingFace logic
│   └── pdf_service.py     # Report generation logic
├── uploads/               # Raw audio storage
└── pdfs/                  # Generated meeting notes

```

---

## 📡 API Reference

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/meetings/` | Upload and process a new recording |
| `GET` | `/meetings/` | List all processed meetings |
| `GET` | `/meetings/{id}` | Retrieve details of a specific meeting |
| `DELETE` | `/meetings/{id}` | Remove a meeting record and files |
| `POST` | `/meetings/{id}/export` | Generate and download PDF notes |
| `GET` | `/meetings/{id}/search` | Query the transcript for specific terms |

---

## ☁️ Deployment Tips

When deploying to platforms like **Render, Railway, or a VPS**:

1. **Dockerize the App**: Use a Dockerfile to ensure a consistent environment containing Python, FFmpeg, and the required Cuda drivers.
2. **System Binaries**: Ensure `ffmpeg` is installed at the system level (`apt install ffmpeg`).
3. **Dependency Management**: Ensure `openai-whisper` and `ffmpeg-python` are explicitly listed in your `requirements.txt`.
4. **Local Testing**: Always test your containerized build locally to verify that Whisper can access the system path for FFmpeg.

---

**Would you like me to generate a professional Dockerfile to accompany this README?**
