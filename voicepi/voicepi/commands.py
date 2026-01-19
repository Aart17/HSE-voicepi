from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class Command:
    id: str
    phrases: List[str]
    pin: int
    action: str
    pulse_ms: int = 300

def load_commands(cfg: Dict[str, Any]) -> List[Command]:
    out = []
    for item in cfg.get("commands", []):
        out.append(Command(
            id=item["id"],
            phrases=[p.lower() for p in item.get("phrases", [])],
            pin=int(item["pin"]),
            action=item["action"].lower(),
            pulse_ms=int(item.get("pulse_ms", 300)),
        ))
    return out

def match_command(text: str, commands: List[Command]) -> Optional[Command]:
    t = (text or "").lower()
    for c in commands:
        if any(ph in t for ph in c.phrases):
            return c
    return None
