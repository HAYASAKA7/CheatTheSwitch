from backend.core.splitter import parse_cheat_content
from backend.core.schemas import ParsedFile


def test_parse_basic_cheats(sample_cheat_content: str):
    result = parse_cheat_content("26CE9F3CC0393826.txt", sample_cheat_content, None)
    assert isinstance(result, ParsedFile)
    assert result.bid == "26CE9F3CC0393826"
    assert result.header == "[Game Header v1.0]"
    assert len(result.cheats) == 3
    assert result.cheats[0].name == "Infinite Health"
    assert len(result.cheats[0].codes) == 3
    assert result.cheats[1].name == "Max Money"
    assert len(result.cheats[1].codes) == 1
    assert result.cheats[2].name == "Infinite Stamina"
    assert len(result.cheats[2].codes) == 3


def test_parse_with_sections(sample_with_sections: str):
    result = parse_cheat_content("ABCD1234ABCD1234.txt", sample_with_sections, None)
    assert len(result.cheats) == 1
    assert result.cheats[0].name == "Infinite Health"


def test_parse_empty_file(empty_cheat_content: str):
    result = parse_cheat_content("ABCD1234ABCD1234.txt", empty_cheat_content, None)
    assert len(result.cheats) == 0
    assert any("No valid cheats" in w.message for w in result.warnings)


def test_parse_bid_warning():
    result = parse_cheat_content("badname.txt", "[H]\n[Cheat]\n04000000 00000000", None)
    assert any("BID" in w.message for w in result.warnings)


def test_parse_with_tid_path():
    result = parse_cheat_content(
        "26CE9F3CC0393826.txt",
        "[H]\n[Cheat]\n04000000 00000000",
        "0100F2C0115B6000/cheats/26CE9F3CC0393826.txt",
    )
    assert result.tid == "0100F2C0115B6000"
