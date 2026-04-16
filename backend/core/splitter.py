import re
from pathlib import Path

from backend.core.schemas import CheatEntry, FileWarning, ParsedFile, SplitResult
from backend.core.game_db import GameDatabase

INVALID_CHARS = re.compile(r'[<>:"/\\|?*]')
BID_PATTERN = re.compile(r'^[0-9A-F]{16}$', re.IGNORECASE)
HEX_CODE_PATTERN = re.compile(r'^[0-9A-F]+( [0-9A-F]+)*$', re.IGNORECASE)
SECTION_PATTERN = re.compile(r'^\[--Section(Start|End):')
CHEAT_NAME_PATTERN = re.compile(r'^\[(.+)\]\s*$')


def sanitize_name(name: str) -> str:
    s = INVALID_CHARS.sub('_', name)
    s = s.strip('. ')
    return s[:200]


def parse_cheat_content(
    filename: str,
    content: str,
    original_path: str | None,
    game_db: GameDatabase | None = None,
) -> ParsedFile:
    warnings: list[FileWarning] = []
    bid = filename.rsplit('.', 1)[0] if '.' in filename else filename

    if not BID_PATTERN.match(bid):
        warnings.append(FileWarning(
            message=f"Filename '{bid}' doesn't look like a valid BID (expected 16 hex chars)"
        ))

    tid: str | None = None
    game_name: str | None = None
    if original_path:
        tid = GameDatabase.detect_tid_from_path(original_path)
    if tid and game_db:
        game_name = game_db.lookup(tid)

    lines = content.splitlines()

    header: str | None = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('[') and not SECTION_PATTERN.match(stripped):
            header = stripped
            break

    if not header:
        header = f"[Cheat BID: {bid}]"
        warnings.append(FileWarning(message=f"Could not detect header, using default: {header}"))

    cheats: list[CheatEntry] = []
    current_name: str | None = None
    current_codes: list[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if SECTION_PATTERN.match(stripped):
            continue
        if stripped == "00000000 00000000 00000000":
            continue

        cheat_match = CHEAT_NAME_PATTERN.match(stripped)
        if cheat_match:
            name = cheat_match.group(1).strip()
            if name.startswith('--Section') or f"[{name}]" == header:
                continue
            if current_name and current_codes:
                cheats.append(CheatEntry(name=current_name, codes=list(current_codes)))
            current_name = name
            current_codes = []
            continue

        if current_name and HEX_CODE_PATTERN.match(stripped):
            current_codes.append(stripped)

    if current_name and current_codes:
        cheats.append(CheatEntry(name=current_name, codes=list(current_codes)))

    if not cheats:
        warnings.append(FileWarning(message="No valid cheats found in the file"))

    return ParsedFile(
        filename=filename,
        bid=bid,
        tid=tid,
        game_name=game_name,
        header=header,
        cheats=cheats,
        warnings=warnings,
    )
