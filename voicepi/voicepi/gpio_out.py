from dataclasses import dataclass
from typing import Dict

from gpiozero import OutputDevice
from .commands import Command

@dataclass
class GpioController:
    active_high: bool = True

    def __post_init__(self):
        self._pins: Dict[int, OutputDevice] = {}

    def _get(self, pin: int) -> OutputDevice:
        if pin not in self._pins:
            self._pins[pin] = OutputDevice(pin, active_high=self.active_high, initial_value=False)
        return self._pins[pin]

    def apply(self, cmd: Command) -> None:
        dev = self._get(cmd.pin)
        if cmd.action == "on":
            dev.on()
        elif cmd.action == "off":
            dev.off()
        elif cmd.action == "pulse":
            dev.on()
            dev.off() if cmd.pulse_ms <= 0 else dev.blink(on_time=cmd.pulse_ms/1000, off_time=0, n=1, background=False)
