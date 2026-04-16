#!/usr/bin/env python3
import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple

# Characters not allowed in Windows folder names
INVALID_CHARS = r'[<>:"/\\|?*]'


def sanitize_name(name: str) -> str:
    """Make a valid Windows folder name from the cheat name."""
    s = re.sub(INVALID_CHARS, '_', name)
    s = s.strip('. ')
    return s[:200]  # Prevent extremely long folder names


def split_cheat_file(file_path: str, output_dir: str = None) -> None:
    """
    Split a Nintendo Switch cheat file into individual cheat folders.

    Expected format:
    - Cheat files are named {BID}.txt
    - Path is usually {TID}/cheats/{BID}.txt
    - Each cheat starts with [Cheat Name] followed by hex code lines
    """
    file_path = Path(file_path).absolute()

    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    # Auto-detect BID from filename
    bid = file_path.stem
    if not re.match(r'^[0-9A-F]{16}$', bid, re.IGNORECASE):
        print(f"Warning: Filename '{bid}' doesn't look like a valid BID (should be 16 hex chars)")

    # Try to detect TID from parent directory structure (if available)
    tid = None
    if file_path.parent.name == "cheats" and re.match(r'^0100[0-9A-F]{12}$', file_path.parent.parent.name, re.IGNORECASE):
        tid = file_path.parent.parent.name
        print(f"Auto-detected TID: {tid}, BID: {bid}")

    # Read the cheat file
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find the header line (usually the first line starting with [)
    header = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('[') and not stripped.startswith('[--Section'):
            header = stripped
            break

    if not header:
        header = f"[Cheat BID: {bid}]"
        print(f"Warning: Could not detect header, using default: {header}")

    # Parse all cheats
    cheats: List[Tuple[str, List[str]]] = []
    current_name = None
    current_codes = []

    for line in lines:
        stripped = line.strip()

        # Skip empty lines and section markers
        if not stripped:
            continue
        if re.match(r'^\[--Section(Start|End):', stripped):
            continue
        if stripped == "00000000 00000000 00000000":  # Separator line
            continue

        # Check if this is a cheat name line
        cheat_match = re.match(r'^\[(.+)\]\s*$', stripped)
        if cheat_match:
            name = cheat_match.group(1).strip()

            # Skip section markers and headers
            if name.startswith('--Section') or stripped == header:
                continue

            # Save previous cheat if valid
            if current_name and current_codes:
                cheats.append((current_name, current_codes))

            current_name = name
            current_codes = []
            continue

        # If we have an active cheat, collect the code lines
        if current_name:
            # Validate it looks like a code line (hex codes separated by spaces)
            if re.match(r'^[0-9A-F]+( [0-9A-F]+)*$', stripped, re.IGNORECASE):
                current_codes.append(stripped)

    # Add the last cheat
    if current_name and current_codes:
        cheats.append((current_name, current_codes))

    if not cheats:
        print("Error: No valid cheats found in the file")
        sys.exit(1)

    print(f"Found {len(cheats)} cheats to split\n")

    # Determine output directory
    if not output_dir:
        output_dir = file_path.parent.parent if (tid and file_path.parent.name == "cheats") else file_path.parent
    output_dir = Path(output_dir)

    # Create each cheat folder
    for name, codes in cheats:
        folder_name = sanitize_name(name)
        cheat_dir = output_dir / folder_name / "cheats"
        cheat_dir.mkdir(parents=True, exist_ok=True)

        out_file = cheat_dir / f"{bid}.txt"
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(f"{header}\n\n")
            f.write(f"[{name}]\n")
            for code in codes:
                f.write(f"{code}\n")

        print(f"  ✓ [{name}] -> {folder_name}/cheats/{bid}.txt ({len(codes)} codes)")

    # Rename the original cheats folder to cheats_backup
    original_cheats_dir = file_path.parent
    if original_cheats_dir.name == "cheats":
        backup_dir = original_cheats_dir.parent / "cheats_backup"
        if backup_dir.exists():
            print(f"\nWarning: cheats_backup already exists at {backup_dir}, skipping rename")
        else:
            original_cheats_dir.rename(backup_dir)
            print(f"\nRenamed '{original_cheats_dir}' -> '{backup_dir}'")

    print(f"\n✅ Success! All {len(cheats)} cheats have been saved to: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="Split Nintendo Switch cheat files into individual cheat folders")
    parser.add_argument("cheat_file", help="Path to the cheat file (usually named with BID like 26CE9F3CC0393826.txt)")
    parser.add_argument("-o", "--output", help="Output directory (defaults to same location as the cheat file or TID folder)")

    args = parser.parse_args()

    split_cheat_file(args.cheat_file, args.output)


if __name__ == "__main__":
    main()
