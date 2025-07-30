# SPDX-License-Identifier: MIT
from dataclasses import dataclass
from io import StringIO
from typing import IO

from .de.parser import ParserError, parse
from .de.scanner import ScannerError, scan
from .errors import MarkedError
from .se.serializer import serialize
from .se.tokenizer import tokenize
from .types import YAMLCollection


@dataclass
class DeserializerError(MarkedError):
    stream: IO[str]

    def __str__(self) -> str:
        return str(self.stream) + "\n" + super().__str__()


def from_stream[T: YAMLCollection](stream: IO[str], *, expect: type[T] = dict):
    try:
        data = parse(scan(stream))
        if not isinstance(data, expect):
            raise TypeError(f"Expected {expect.__name__}, got {type(data).__name__}")
        return data
    except (ParserError, ScannerError) as e:
        raise DeserializerError(e.problem, e.mark, stream)
    except Exception as e:
        print(stream)
        raise e


def from_string[T: YAMLCollection](source: str, expect: type[T]):
    stream = StringIO(source)
    return from_stream(stream, expect=expect)


def to_stream(stream: IO[str], data: YAMLCollection) -> None:
    serialize(stream, tokenize(data))


def to_string(data: YAMLCollection) -> str:
    stream = StringIO()
    to_stream(stream, data)
    return stream.getvalue()
