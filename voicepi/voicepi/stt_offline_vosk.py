import json
from dataclasses import dataclass
from pathlib import Path

from vosk import Model, KaldiRecognizer

@dataclass
class VoskStt:
    model_dir: str
    sample_rate: int = 16000

    def __post_init__(self):
        p = Path(self.model_dir)
        if not p.exists():
            raise RuntimeError(f"Vosk model_dir not found: {p}")
        self.model = Model(str(p))

    def transcribe(self, pcm16le_mono: bytes) -> str:
        rec = KaldiRecognizer(self.model, self.sample_rate)
        rec.SetWords(False)
        rec.AcceptWaveform(pcm16le_mono)
        res = json.loads(rec.FinalResult())
        return (res.get("text") or "").strip()
