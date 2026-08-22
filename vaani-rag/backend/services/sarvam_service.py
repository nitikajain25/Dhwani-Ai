import os
import time
import base64
from typing import Tuple, Dict, Any

from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

class SarvamService:
    def __init__(self):
        api_key = os.getenv("SARVAM_API_KEY")
        if not api_key:
            raise ValueError("SARVAM_API_KEY environment variable is not set.")
        self.client = SarvamAI(api_subscription_key=api_key)

    def transcribe(self, audio_data: bytes, language_code: str = "unknown") -> Tuple[str, str, float]:
        """
        Returns: (transcript, detected_language, latency_ms)
        """
        t0 = time.time()
        
        response = self.client.speech_to_text.transcribe(
            file=audio_data,
            model="saaras:v3",
            mode="transcribe",
            language_code=language_code
        )
        latency = (time.time() - t0) * 1000.0
        
        # Parse the response data
        # Depending on SDK, it could be response.transcript or response.data.transcript
        # A typical transcription response:
        transcript = ""
        detected_language = language_code
        if hasattr(response, 'data') and response.data:
            data = response.data[0] if isinstance(response.data, list) else response.data
            transcript = getattr(data, 'transcript', getattr(data, 'text', ''))
            detected_language = getattr(data, 'language_code', detected_language)
        elif hasattr(response, 'transcript'):
            transcript = response.transcript
            detected_language = getattr(response, 'language_code', detected_language)
            
        return transcript, detected_language, latency

    def synthesize(self, text: str, language_code: str = "hi-IN", speaker: str = "ritu") -> Tuple[bytes, float]:
        """
        Returns: (audio_bytes, latency_ms)
        """
        t0 = time.time()
        response = self.client.text_to_speech.convert(
            text=text,
            language_code=language_code,
            speaker=speaker,
            model="bulbul:v3"
        )
        latency = (time.time() - t0) * 1000.0
        
        # Audio is usually returned as base64 string in audios attribute
        # or as raw bytes
        if hasattr(response, 'audios') and response.audios:
            audio_b64 = response.audios[0]
            audio_bytes = base64.b64decode(audio_b64)
            return audio_bytes, latency
        return b"", latency

sarvam_service = None
def get_sarvam_service():
    global sarvam_service
    if sarvam_service is None:
        sarvam_service = SarvamService()
    return sarvam_service
