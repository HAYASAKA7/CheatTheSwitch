from dataclasses import dataclass, field


@dataclass(frozen=True)
class CheatEntry:
    name: str
    codes: list[str]


@dataclass(frozen=True)
class FileWarning:
    message: str


@dataclass(frozen=True)
class ParsedFile:
    filename: str
    bid: str
    tid: str | None
    game_name: str | None
    header: str
    cheats: list[CheatEntry]
    warnings: list[FileWarning]


@dataclass(frozen=True)
class SplitRequest:
    files: list[ParsedFile]
    output_template: str = "{game}/{cheat}/cheats/{bid}.txt"
    selected_cheats: dict[str, list[str]] = field(default_factory=dict)


@dataclass(frozen=True)
class SplitResult:
    filename: str
    cheats_written: int
    output_paths: list[str]
    errors: list[str]
