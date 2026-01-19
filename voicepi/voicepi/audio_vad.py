import collections
import time
from dataclasses import dataclass
from typing import Iterable, Optional

import sounddevice as sd
import webrtcvad

@dataclass
class VadConfig:
    sample_rate: int = 16000
    vad_aggressiveness: int = 2
    max_utterance_sec: int = 6
    device_hint: str = ""

def _pick_input_device(device_hint: str) -> Optional[int]:
    if not device_hint:
        return None
    hint = device_hint.lower()
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        if d.get("max_input_channels", 0) > 0 and hint in str(d.get("name", "")).lower():
            return i
    return None

def iter_utterances(cfg: VadConfig) -> Iterable[bytes]:
    sr = cfg.sample_rate
    vad = webrtcvad.Vad(cfg.vad_aggressiveness)

    frame_ms = 30
    frame_samples = int(sr * frame_ms / 1000)
    frame_bytes = frame_samples * 2  # int16 mono
    padding_ms = 450
    padding_frames = int(padding_ms / frame_ms)

    dev = _pick_input_device(cfg.device_hint)

    ring = collections.deque(maxlen=padding_frames)
    triggered = False
    voiced = bytearray()
    last_voice_ts = time.time()

    def is_speech(frame: bytes) -> bool:
        if len(frame) != frame_bytes:
            return False
        return vad.is_speech(frame, sr)

    with sd.RawInputStream(
        samplerate=sr,
        blocksize=frame_samples,
        dtype="int16",
        channels=1,
        device=dev,
    ) as stream:
        while True:
            data, _ = stream.read(frame_samples)
            frame = bytes(data)

            speech = is_speech(frame)
            now = time.time()

            if not triggered:
                ring.append((frame, speech))
                if sum(1 for _, s in ring if s) > int(0.6 * ring.maxlen):
                    triggered = True
                    for f, _ in ring:
                        voiced.extend(f)
                    ring.clear()
                    last_voice_ts = now
            else:
                voiced.extend(frame)
                if speech:
                    last_voice_ts = now

                if (now - last_voice_ts) > 0.6:
                    yield bytes(voiced)
                    voiced.clear()
                    ring.clear()
                    triggered = False

                if len(voiced) > cfg.max_utterance_sec * sr * 2:
                    yield bytes(voiced)
                    voiced.clear()
                    ring.clear()
                    triggered = False
