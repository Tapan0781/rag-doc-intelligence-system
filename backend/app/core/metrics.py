from __future__ import annotations

from typing import Dict

_COUNTERS: Dict[str, int] = {}


def inc(name: str, value: int = 1) -> None:
    _COUNTERS[name] = _COUNTERS.get(name, 0) + value


def snapshot() -> Dict[str, int]:
    return dict(_COUNTERS)
