#!/usr/bin/env python3
import re
from pathlib import Path
from typing import List, Tuple

INVALID_CHARS = r'[<>:"/\\|?*]'


def sanitize_name(name: str) -> str:
    s = re.sub(INVALID_CHARS, '_', name)
    s = s.strip('. ')
    return s[:200]


def detect_tid(file_path: Path) -> str | None:
    if file_path.parent.name != "cheats":
        return None
    candidate = file_path.parent.parent.name
    if re.match(r'^0100[0-9A-F]{12}$', candidate, re.IGNORECASE):
        return candidate
    return None


def suggest_output_dir(file_path: str | Path) -> Path:
    path = Path(file_path).absolute()
    tid = detect_tid(path)
    game_name_or_id = tid or path.parent.name or path.stem
    return path.parent / game_name_or_id


def output_subfolder_name(file_path: str | Path) -> str:
    path = Path(file_path).absolute()
    tid = detect_tid(path)
    return tid or path.parent.name or path.stem


def _parse_cheats(file_path: Path, bid: str) -> tuple[str, List[Tuple[str, List[str]]]]:
    with file_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    header = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('[') and not stripped.startswith('[--Section'):
            header = stripped
            break
    if not header:
        header = f"[Cheat BID: {bid}]"

    cheats: List[Tuple[str, List[str]]] = []
    current_name = None
    current_codes: List[str] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r'^\[--Section(Start|End):', stripped):
            continue
        if stripped == "00000000 00000000 00000000":
            continue

        cheat_match = re.match(r'^\[(.+)\]\s*$', stripped)
        if cheat_match:
            name = cheat_match.group(1).strip()
            if name.startswith('--Section') or stripped == header:
                continue

            if current_name and current_codes:
                cheats.append((current_name, current_codes))

            current_name = name
            current_codes = []
            continue

        if current_name and re.match(r'^[0-9A-F]+( [0-9A-F]+)*$', stripped, re.IGNORECASE):
            current_codes.append(stripped)

    if current_name and current_codes:
        cheats.append((current_name, current_codes))

    return header, cheats


def split_cheat_file(
    file_path: str | Path,
    output_dir: str | Path | None = None,
    backup_original: bool = True,
) -> List[str]:
    logs: List[str] = []
    path = Path(file_path).absolute()

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    bid = path.stem
    if not re.match(r'^[0-9A-F]{16}$', bid, re.IGNORECASE):
        logs.append(f"Warning: filename '{bid}' does not look like a BID (16 hex chars).")

    tid = detect_tid(path)
    if tid:
        logs.append(f"Detected game id (TID): {tid}, BID: {bid}")

    header, cheats = _parse_cheats(path, bid)
    if header == f"[Cheat BID: {bid}]":
        logs.append(f"Warning: could not detect header, using default: {header}")

    if not cheats:
        raise ValueError("No valid cheats found in the file")

    out_root = Path(output_dir).absolute() if output_dir else suggest_output_dir(path)
    logs.append(f"Found {len(cheats)} cheats.")

    for name, codes in cheats:
        folder_name = sanitize_name(name)
        cheat_dir = out_root / folder_name / "cheats"
        cheat_dir.mkdir(parents=True, exist_ok=True)

        out_file = cheat_dir / f"{bid}.txt"
        with out_file.open("w", encoding="utf-8") as f:
            f.write(f"{header}\n\n")
            f.write(f"[{name}]\n")
            for code in codes:
                f.write(f"{code}\n")

        logs.append(f"OK [{name}] -> {out_file} ({len(codes)} code lines)")

    if backup_original and path.parent.name == "cheats":
        backup_dir = path.parent.parent / "cheats_backup"
        if backup_dir.exists():
            logs.append(f"Warning: backup folder already exists, skipped rename: {backup_dir}")
        else:
            old_dir = path.parent
            old_dir.rename(backup_dir)
            logs.append(f"Renamed '{old_dir}' -> '{backup_dir}'")

    logs.append(f"Success. Output saved to: {out_root}")
    return logs
