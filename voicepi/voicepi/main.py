import time
from pathlib import Path
import yaml

from audio_vad import VadConfig, iter_utterances
from commands import load_commands, match_command
from gpio_out import GpioController
from net import can_reach_google_stt
from stt_offline_vosk import VoskStt
from stt_online_google import GoogleStt

def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def main():
    cfg_path = str(Path(__file__).resolve().parent.parent / "config.yaml")
    cfg = load_config(cfg_path)

    vad_cfg = VadConfig(**cfg.get("audio", {}))
    commands = load_commands(cfg)
    gpio = GpioController(active_high=bool(cfg.get("gpio", {}).get("active_high", True)))

    mode = (cfg.get("mode") or "auto").lower()

    vosk = VoskStt(model_dir=cfg["vosk"]["model_dir"], sample_rate=vad_cfg.sample_rate)

    google = None
    if cfg.get("google", {}).get("enabled", True):
        try:
            google = GoogleStt(
                credentials_json=cfg["google"]["credentials_json"],
                language_code=cfg["google"].get("language_code", "ru-RU"),
                sample_rate=vad_cfg.sample_rate,
                timeout_sec=int(cfg["google"].get("timeout_sec", 8)),
            )
        except Exception:
            google = None

    for utt in iter_utterances(vad_cfg):
        text = ""

        use_google = (
            mode in ("auto", "online")
            and google is not None
            and can_reach_google_stt()
        )

        if mode == "offline":
            use_google = False
        if mode == "online":
            use_google = True and (google is not None) and can_reach_google_stt()

        try:
            text = google.transcribe(utt) if use_google else vosk.transcribe(utt)
        except Exception:
            text = ""

        if not text:
            continue

        cmd = match_command(text, commands)
        if cmd:
            print(cmd)
            gpio.apply(cmd)
        time.sleep(0.05)

if __name__ == "__main__":
    main()
