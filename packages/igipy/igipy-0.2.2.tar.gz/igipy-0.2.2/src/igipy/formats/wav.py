import wave
from io import BytesIO
from struct import Struct
from typing import ClassVar, Literal, Self

from pydantic import NonNegativeInt

from . import base
from .utils import adpcm


class WAV(base.FileModel):
    header: "WAVHeader"
    content: bytes

    @classmethod
    def model_validate_stream(cls, stream: BytesIO) -> Self:
        header = WAVHeader.model_validate_stream(stream)
        content = stream.read()
        return cls(header=header, content=content)

    @property
    def samples(self) -> bytes:
        if self.header.sound_pack in {0, 1}:
            return self.content
        if self.header.sound_pack in {2, 3}:
            return adpcm.decode(self.content, channels=self.header.channels)

        raise ValueError(f"Unsupported sound pack: {self.header.sound_pack}")

    def model_dump_stream(self) -> tuple[BytesIO, str]:
        stream = BytesIO()
        samples = self.samples

        with wave.open(stream, "w") as wave_stream:
            wave_stream.setnchannels(self.header.channels)
            wave_stream.setsampwidth(self.header.sample_width // 8)
            wave_stream.setframerate(self.header.framerate)
            wave_stream.writeframesraw(samples)

        return stream, ".wav"


class WAVHeader(base.StructModel):
    struct: ClassVar[Struct] = Struct("4s4H2I")

    signature: Literal[b"ILSF"]
    sound_pack: Literal[0, 1, 2, 3]
    sample_width: Literal[16]
    channels: Literal[1, 2]
    unknown: NonNegativeInt
    framerate: Literal[11025, 22050, 44100]
    sample_count: NonNegativeInt
