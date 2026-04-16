import json
import re
from dataclasses import dataclass
from pathlib import Path


TID_PATTERN = re.compile(r'(0100[0-9A-Fa-f]{12})')


@dataclass(frozen=True)
class GameDatabase:
    _entries: dict[str, str]

    @staticmethod
    def from_json(path: Path) -> "GameDatabase":
        with open(path, "r", encoding="utf-8") as f:
            raw: dict[str, str] = json.load(f)
        normalized = {k.upper(): v for k, v in raw.items()}
        return GameDatabase(_entries=normalized)

    def lookup(self, tid: str) -> str | None:
        return self._entries.get(tid.upper())

    @staticmethod
    def detect_tid_from_path(path_str: str) -> str | None:
        match = TID_PATTERN.search(path_str)
        return match.group(1).upper() if match else None
