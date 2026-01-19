from dataclasses import dataclass
from pathlib import Path

from google.cloud import speech

@dataclass
class GoogleStt:
    credentials_json: str
    language_code: str = "ru-RU"
    sample_rate: int = 16000
    timeout_sec: int = 8

    def __post_init__(self):
        p = Path(self.credentials_json)
        if not p.exists():
            raise RuntimeError(f"GCP credentials file not found: {p}")
        self.client = speech.SpeechClient.from_service_account_file(str(p))

    def transcribe(self, pcm16le_mono: bytes) -> str:
        audio = speech.RecognitionAudio(content=pcm16le_mono)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.sample_rate,
            language_code=self.language_code,
        )
        resp = self.client.recognize(config=config, audio=audio, timeout=self.timeout_sec)
        if not resp.results:
            return ""
        return (resp.results[0].alternatives[0].transcript or "").strip()
