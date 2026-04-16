from backend.core.schemas import CheatEntry, ParsedFile, SplitRequest, SplitResult, FileWarning


def test_cheat_entry_creation():
    entry = CheatEntry(name="Infinite Health", codes=["580F0000 0256B684", "780F0000 00000000"])
    assert entry.name == "Infinite Health"
    assert len(entry.codes) == 2


def test_parsed_file_creation():
    cheats = [CheatEntry(name="Infinite Health", codes=["580F0000 0256B684"])]
    parsed = ParsedFile(
        filename="26CE9F3CC0393826.txt",
        bid="26CE9F3CC0393826",
        tid=None,
        game_name=None,
        header="[Cheat BID: 26CE9F3CC0393826]",
        cheats=cheats,
        warnings=[],
    )
    assert parsed.bid == "26CE9F3CC0393826"
    assert parsed.tid is None
    assert len(parsed.cheats) == 1


def test_parsed_file_with_tid():
    parsed = ParsedFile(
        filename="26CE9F3CC0393826.txt",
        bid="26CE9F3CC0393826",
        tid="0100F2C0115B6000",
        game_name="Zelda TOTK",
        header="[Header]",
        cheats=[],
        warnings=[FileWarning(message="No cheats found")],
    )
    assert parsed.tid == "0100F2C0115B6000"
    assert parsed.game_name == "Zelda TOTK"
    assert len(parsed.warnings) == 1


def test_split_request_defaults():
    req = SplitRequest(
        files=[ParsedFile(
            filename="test.txt", bid="AAAA", tid=None,
            game_name=None, header="[H]", cheats=[], warnings=[],
        )],
    )
    assert req.output_template == "{game}/{cheat}/cheats/{bid}.txt"
    assert req.selected_cheats == {}


def test_split_result():
    result = SplitResult(
        filename="test.txt",
        cheats_written=3,
        output_paths=["GameA/Cheat1/cheats/BID.txt"],
        errors=[],
    )
    assert result.cheats_written == 3
