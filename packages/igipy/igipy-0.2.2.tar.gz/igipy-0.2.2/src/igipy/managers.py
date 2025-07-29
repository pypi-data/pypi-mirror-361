import zipfile
from collections.abc import Generator
from io import BytesIO
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, PlainSerializer, field_validator

PosixPath = Annotated[Path, PlainSerializer(lambda value: value.as_posix(), return_type=str, when_used="json")]


class BaseManager(BaseModel):
    pass


class IGI1Manager(BaseManager):
    source_dir: PosixPath = Path("C:/Games/ProjectIGI")
    unpack_dir: PosixPath = Path("./unpack")
    target_dir: PosixPath = Path("./target")

    # noinspection PyNestedDecorators
    @field_validator("source_dir", mode="after")
    @classmethod
    def is_game_dir(cls, value: Path) -> Path:
        if not value.is_dir():
            raise ValueError(f"{value.as_posix()} is not a directory")

        if not (value / "igi.exe").is_file(follow_symlinks=False):
            raise ValueError(f"igi.exe not found in {value.as_posix()}")

        return value

    # noinspection PyNestedDecorators
    @field_validator("unpack_dir", "target_dir", mode="after")
    @classmethod
    def is_work_dir(cls, value: Path) -> Path:
        if not value.exists():
            value.mkdir(parents=True)

        if not value.is_dir():
            raise ValueError(f"{value.as_posix()} is not a directory")

        return value

    def read_from_source(self, patterns: list[str]) -> Generator[tuple[BytesIO, Path, None]]:
        for src_path in self.source_dir.glob("**/*"):
            if src_path.is_file(follow_symlinks=False) and any(src_path.match(pattern) for pattern in patterns):
                yield BytesIO(src_path.read_bytes()), src_path.relative_to(self.source_dir), None

    def read_from_unpack(self, patterns: list[str]) -> Generator[tuple[BytesIO, Path, Path]]:
        for zip_path in self.unpack_dir.glob("**/*.zip"):
            with zipfile.ZipFile(zip_path, "r") as zip_file:
                for file_info in zip_file.infolist():
                    src_path = Path(file_info.filename)

                    if any(src_path.match(pattern) for pattern in patterns):
                        src_stream = BytesIO(zip_file.read(file_info))
                        yield src_stream, src_path, zip_path.relative_to(self.unpack_dir)

    def read_all_res(self) -> Generator[tuple[BytesIO, Path, Path | None]]:
        yield from self.read_from_source(patterns=["**/*.res"])

    def read_all_wav(self) -> Generator[tuple[BytesIO, Path, Path | None]]:
        yield from self.read_from_source(patterns=["**/*.wav"])
        yield from self.read_from_unpack(patterns=["**/*.wav"])

    def read_all_qvm(self) -> Generator[tuple[BytesIO, Path, Path | None]]:
        yield from self.read_from_source(patterns=["**/*.qvm"])

    def read_all_tex(self) -> Generator[tuple[BytesIO, Path, Path | None]]:
        yield from self.read_from_source(patterns=["**/*.tex", "**/*.spr", "**/*.pic"])
        yield from self.read_from_unpack(patterns=["**/*.tex", "**/*.spr", "**/*.pic"])

    def read_all_mef(self) -> Generator[tuple[BytesIO, Path, Path | None]]:
        yield from self.read_from_unpack(patterns=["**/*.mef"])
