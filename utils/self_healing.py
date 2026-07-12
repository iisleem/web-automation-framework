from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LocatorCandidate:
    selector: str
    description: str
