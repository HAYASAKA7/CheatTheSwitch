import pytest

SAMPLE_CHEAT_CONTENT = """[Game Header v1.0]

[Infinite Health]
580F0000 0256B684
780F0000 00000000
640F0000 00000000 3F800000

[Max Money]
04000000 0256B688 05F5E0FF

[Infinite Stamina]
580F0000 0256B690
780F0000 00000000
640F0000 00000000 42480000
"""

SAMPLE_WITH_SECTIONS = """[--SectionStart:Main]
[Game Header v1.0]

[Infinite Health]
580F0000 0256B684

[--SectionEnd:Main]
"""

EMPTY_CHEAT_CONTENT = """[Game Header v1.0]
"""


@pytest.fixture
def sample_cheat_content() -> str:
    return SAMPLE_CHEAT_CONTENT


@pytest.fixture
def sample_with_sections() -> str:
    return SAMPLE_WITH_SECTIONS


@pytest.fixture
def empty_cheat_content() -> str:
    return EMPTY_CHEAT_CONTENT
