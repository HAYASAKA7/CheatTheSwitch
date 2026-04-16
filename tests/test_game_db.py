import json
from pathlib import Path
from backend.core.game_db import GameDatabase


def test_load_from_json(tmp_path: Path):
    seed = {"0100F2C0115B6000": "Zelda TOTK", "010028600EBDA000": "Mario Odyssey"}
    seed_file = tmp_path / "seed.json"
    seed_file.write_text(json.dumps(seed))
    db = GameDatabase.from_json(seed_file)
    assert db.lookup("0100F2C0115B6000") == "Zelda TOTK"


def test_lookup_missing_returns_none(tmp_path: Path):
    seed_file = tmp_path / "seed.json"
    seed_file.write_text("{}")
    db = GameDatabase.from_json(seed_file)
    assert db.lookup("AAAAAAAAAAAAAAAA") is None


def test_lookup_case_insensitive(tmp_path: Path):
    seed = {"0100F2C0115B6000": "Zelda TOTK"}
    seed_file = tmp_path / "seed.json"
    seed_file.write_text(json.dumps(seed))
    db = GameDatabase.from_json(seed_file)
    assert db.lookup("0100f2c0115b6000") == "Zelda TOTK"


def test_detect_tid_from_path():
    path_str = "0100F2C0115B6000/cheats/26CE9F3CC0393826.txt"
    tid = GameDatabase.detect_tid_from_path(path_str)
    assert tid == "0100F2C0115B6000"


def test_detect_tid_no_match():
    tid = GameDatabase.detect_tid_from_path("random/folder/cheat.txt")
    assert tid is None
