import os
import json
import time
import base64
import hmac
import hashlib
import uuid
from datetime import datetime
import aiohttp
import asyncio
from typing import Dict, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Alibaba Cloud ASR configuration
ACCESS_KEY_ID = os.environ.get("ALIBABA_ACCESS_KEY_ID")
ACCESS_KEY_SECRET = os.environ.get("ALIBABA_ACCESS_KEY_SECRET")
APP_KEY = os.environ.get("ALIBABA_APP_KEY")
API_ENDPOINT = "https://nls-gateway.cn-shanghai.aliyuncs.com/stream/v1/asr"

# Language mapping for Alibaba ASR
LANGUAGE_MAPPING = {
    "english": "en-US",
    "mandarin": "zh-CN",
    "cantonese": "zh-HK",
    "mixed": "zh-CN",  # Default to Mandarin for mixed, will handle special case
}

async def get_token() -> str:
    """Get Alibaba Cloud access token"""
    if not ACCESS_KEY_ID or not ACCESS_KEY_SECRET:
        raise ValueError("Alibaba Cloud credentials not set in environment variables")
    
    # Alibaba Cloud token endpoint
    token_url = "https://nls-meta.cn-shanghai.aliyuncs.com/pop/2018-05-18/tokens"
    
    # Current timestamp in ISO format
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Generate signature
    request_params = {
        "AccessKeyId": ACCESS_KEY_ID,
        "Action": "CreateToken",
        "Format": "JSON",
        "RegionId": "cn-shanghai",
        "SignatureMethod": "HMAC-SHA1",
        "SignatureNonce": str(uuid.uuid4()),
        "SignatureVersion": "1.0",
        "Timestamp": timestamp,
        "Version": "2018-05-18"
    }
    
    # Sort parameters
    sorted_params = sorted(request_params.items(), key=lambda x: x[0])
    
    # Create canonicalized query string
    canonicalized_query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
    
    # Create string to sign
    string_to_sign = f"GET&%2F&{canonicalized_query_string}"
    
    # Calculate signature
    key = f"{ACCESS_KEY_SECRET}&"
    signature = base64.b64encode(
        hmac.new(key.encode('utf-8'), string_to_sign.encode('utf-8'), hashlib.sha1).digest()
    ).decode('utf-8')
    
    # Add signature to parameters
    request_params["Signature"] = signature
    
    # Make request
    async with aiohttp.ClientSession() as session:
        async with session.get(token_url, params=request_params) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"Failed to get token: {error_text}")
                raise ValueError(f"Failed to get token: {response.status}")
            
            data = await response.json()
            if "Token" not in data:
                logger.error(f"Invalid token response: {data}")
                raise ValueError(f"Invalid token response: {data}")
            
            return data["Token"]["Id"]

async def transcribe_audio(file_path: str, language: str) -> str:
    """
    Transcribe audio using Alibaba Cloud ASR
    
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
    
    # Get token
    token = await get_token()
    logger.info(f"Got token: {token[:10]}...")
    
    # Prepare API request with proper language setting
    alibaba_language = LANGUAGE_MAPPING.get(language.lower(), "en-US")
    
    # For long audio files, we need to use the FileTranscription API
    # This is a simplified implementation - in production, you might want to use
    # the asynchronous API for very long files
    
    # Read audio file
    with open(file_path, "rb") as f:
        audio_content = f.read()
    
    # Convert to base64
    audio_base64 = base64.b64encode(audio_content).decode('utf-8')
    
    # Prepare request payload
    payload = {
        "audio": audio_base64,
        "format": os.path.splitext(file_path)[1][1:].lower(),  # Get format from file extension
        "sample_rate": 16000,  # Assuming 16kHz audio
        "enable_punctuation": True,
        "enable_inverse_text_normalization": True,
        "language": alibaba_language
    }
    
    # API endpoint for file transcription
    file_transcription_url = "https://nls-gateway.cn-shanghai.aliyuncs.com/rest/v1/asr"
    
    # Headers
    headers = {
        "X-NLS-Token": token,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Make request
    async with aiohttp.ClientSession() as session:
        async with session.post(file_transcription_url, json=payload, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"Failed to transcribe audio: {error_text}")
                raise ValueError(f"Failed to transcribe audio: {response.status}")
            
            data = await response.json()
            if "result" not in data:
                logger.error(f"Invalid transcription response: {data}")
                raise ValueError(f"Invalid transcription response: {data}")
            
            return data["result"]

async def transcribe_audio_streaming(file_path: str, language: str) -> str:
    """
    Transcribe audio using Alibaba Cloud ASR streaming API
    This is useful for real-time transcription or very large files
    
    Args:
        file_path: Path to the audio file
        language: Language of the audio (english, mandarin, cantonese, mixed)
        
    Returns:
        Transcription text
    """
    # Get token
    token = await get_token()
    
    # Prepare API request with proper language setting
    alibaba_language = LANGUAGE_MAPPING.get(language.lower(), "en-US")
    
    # Streaming API endpoint
    streaming_url = f"{API_ENDPOINT}?appkey={APP_KEY}&token={token}&format=wav&sample_rate=16000"
    
    # Read audio file in chunks
    chunk_size = 1024 * 16  # 16KB chunks
    transcription_results = []
    
    with open(file_path, "rb") as f:
        # Create WebSocket connection
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(streaming_url) as ws:
                # Send audio data in chunks
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                    await ws.send_bytes(chunk)
                    await asyncio.sleep(0.1)  # Small delay to simulate real-time
                    
                    # Check for responses
                    try:
                        msg = await ws.receive(timeout=0.1)
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            if "result" in data:
                                transcription_results.append(data["result"])
                    except asyncio.TimeoutError:
                        pass
                
                # Send end of stream
                await ws.send_bytes(b"")
                
                # Get final results
                try:
                    while True:
                        msg = await ws.receive(timeout=5.0)
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            if "result" in data:
                                transcription_results.append(data["result"])
                        elif msg.type == aiohttp.WSMsgType.CLOSED:
                            break
                except (asyncio.TimeoutError, aiohttp.ClientError):
                    pass
    
    # Combine results
    return " ".join(transcription_results)

async def detect_speakers(transcript: str) -> list:
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
