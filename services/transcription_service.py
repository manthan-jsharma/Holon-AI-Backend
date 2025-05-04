import os

from typing import Dict, Any, Optional, List
import logging
import whisper
import torch


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Whisper model configuration
WHISPER_MODEL_SIZE = os.environ.get("WHISPER_MODEL_SIZE", "tiny")  # Options: tiny, base, small, medium, large
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Cache for loaded model
_model = None

def get_whisper_model():
    """Get or load the Whisper model"""
    global _model
    if _model is None:
        logger.info(f"Loading Whisper model: {WHISPER_MODEL_SIZE} on {DEVICE}")
        _model = whisper.load_model(WHISPER_MODEL_SIZE, device=DEVICE)
        logger.info(f"Whisper model loaded successfully")
    return _model

async def transcribe_audio(file_path: str, language: str) -> str:
    """
    Transcribe audio using locally installed Whisper
    
    Args:
        file_path: Path to the audio file
        language: Language of the audio (english, mandarin, cantonese, mixed)
        
    Returns:
        Transcription text
    """
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    # Get file size
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        raise ValueError("Audio file is empty")
    
    # Map language to Whisper language code
    language_mapping = {
        "english": "en",
        "mandarin": "zh",
        "cantonese": "zh",  # Whisper doesn't have specific Cantonese support, using zh
        "mixed": None,  # Let Whisper auto-detect for mixed
    }
    
    whisper_language = language_mapping.get(language.lower())
    
    try:
        # Get the model
        model = get_whisper_model()
        
        # Transcribe audio
        logger.info(f"Starting transcription of {file_path} with language: {language}")
        
        # Set transcription options
        transcribe_options = {
            "fp16": DEVICE == "cuda",  # Use fp16 if on GPU
            "verbose": True,
        }
        
        # Add language if specified (not mixed)
        if whisper_language:
            transcribe_options["language"] = whisper_language
        
        # Perform transcription
        result = model.transcribe(file_path, **transcribe_options)
        
        logger.info(f"Transcription completed successfully")
        
        # Return the transcribed text
        return result["text"]
        
    except Exception as e:
        logger.error(f"Error in transcription: {e}")
        raise ValueError(f"Failed to transcribe audio: {str(e)}")

async def detect_speakers(transcript: str) -> List[Dict[str, str]]:
    """
    Detect speakers from transcript
    
    Args:
        transcript: Transcription text
        
    Returns:
        List of speakers
    """
    speakers = set()
    
    # Simple regex to extract names from transcript
    lines = transcript.strip().split('\n')
    for line in lines:
        if ':' in line:
            name = line.split(':', 1)[0].strip()
            if name:
                speakers.add(name)
    
    return [{"name": name} for name in speakers]

