"""Independent Python oracle for the frozen K1 Serial Studio parser schema 1.2."""

from __future__ import annotations

import math
import re


class LegacyK1ParserV12:
    """Stateful, per-source reproduction of `k1_observe_v1_2.js`."""

    def __init__(self) -> None:
        self.last: list[float] = [0.0] * 24
        self.parse_seq = 0
        self.mask = 0

    @staticmethod
    def _kv(frame: str, key: str) -> float | None:
        match = re.search(
            rf"(?:^|[\s,|]){re.escape(key)}=(-?[0-9]+(?:\.[0-9]+)?)", frame
        )
        return float(match.group(1)) if match else None

    def _set_kv(self, frame: str, key: str, index: int) -> None:
        value = self._kv(frame, key)
        if value is not None and math.isfinite(value):
            self.last[index] = value
            self.mask |= 1 << index

    def _recompute_orbit(self, frame: str) -> None:
        self._set_kv(frame, "phase", 21)
        peak = self.last[8]
        phase = self.last[21]
        self.last[22] = peak * math.cos(2 * math.pi * phase)
        self.last[23] = peak * math.sin(2 * math.pi * phase)
        self.mask |= (1 << 22) | (1 << 23)

    def _publish(self, kind: int) -> list[float]:
        self.parse_seq += 1
        self.last[17] = float(self.parse_seq)
        self.last[19] = float(kind)
        self.mask |= (1 << 17) | (1 << 19) | (1 << 20)
        self.last[20] = float(self.mask)
        return self.last.copy()

    def parse(self, frame: str | object) -> list[float]:
        value = frame if isinstance(frame, str) else ""
        value = value.replace("\r", "").strip()
        if not value:
            return []
        self.mask = 0

        if value.startswith("[AP]"):
            boundary = ord(value[4]) if len(value) > 4 else 32
            if len(value) == 4 or boundary in {32, 9, 44, 124}:
                for key, index in (
                    ("bpm", 0),
                    ("conf", 1),
                    ("lock", 2),
                    ("beat", 3),
                    ("onset", 4),
                    ("bass", 5),
                    ("silence", 6),
                    ("agc_gain", 7),
                    ("peak_scaled", 8),
                    ("SSL", 9),
                    ("lightshow", 14),
                ):
                    self._set_kv(value, key, index)
                self._recompute_orbit(value)
                return self._publish(1)

        if value.startswith("EVENT_STATUS"):
            for key, index in (
                ("beat", 3),
                ("onset", 4),
                ("bass", 5),
                ("sil", 6),
                ("energy", 10),
                ("nov", 11),
                ("conf", 1),
                ("t", 15),
                ("frame_ms", 16),
                ("tid", 18),
            ):
                self._set_kv(value, key, index)
            self._recompute_orbit(value)
            return self._publish(2)

        if value.startswith("SYSTEM_FPS:"):
            remainder = value[11:].strip()
            try:
                fps = float(remainder)
            except ValueError:
                return []
            if not remainder or not math.isfinite(fps):
                return []
            self.last[12] = fps
            self.mask |= 1 << 12
            return self._publish(3)

        if value.startswith("LED_FPS:"):
            remainder = value[8:].strip()
            try:
                led_fps = float(remainder)
            except ValueError:
                return []
            if not remainder or not math.isfinite(led_fps):
                return []
            self.last[13] = led_fps
            self.mask |= 1 << 13
            return self._publish(4)

        if value.startswith("VERSION:"):
            return self._publish(5)
        return []
