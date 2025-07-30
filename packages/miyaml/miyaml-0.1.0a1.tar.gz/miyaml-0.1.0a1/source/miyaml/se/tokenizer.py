# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field

from ..tokens import (
    KeyBlockToken,
    KeyMultiToken,
    KeyValueToken,
    Mark,
    SequenceBlockToken,
    SequenceMultiToken,
    SequenceValueToken,
)
from ..types import TokenGenerator, YAMLCollection, YAMLMapping, YAMLSequence


@dataclass
class Tokenizer:
    o: YAMLCollection

    line: int = 1

    indents: list[int] = field(default_factory=list)

    @property
    def column(self) -> int:
        return sum(self.indents) + 1

    @property
    def mark(self) -> Mark:
        return Mark(line=self.line, column=self.column)

    def tokenize(self) -> TokenGenerator:
        value = self.o
        match value:
            case dict():
                yield from self.handle_mapping(value)
            case list():
                yield from self.handle_sequence(value)
            case _:
                raise ValueError(f"{value}, {type(value)}")

    def handle_mapping(self, o: YAMLMapping) -> TokenGenerator:
        for key, value in o.items():
            match value:
                case dict():
                    yield KeyBlockToken(key=key, mark=self.mark)
                    self.line += 1
                    self.indents.append(4)
                    yield from self.handle_mapping(value)
                    self.indents.pop()
                case list():
                    yield KeyBlockToken(key=key, mark=self.mark)
                    self.line += 1
                    self.indents.append(4)
                    yield from self.handle_sequence(value)
                    self.indents.pop()
                case str():
                    key_mark = self.mark
                    lines = value.splitlines()
                    if len(lines) == 1:
                        yield KeyValueToken(key=key, value=value, mark=key_mark)
                    else:
                        self.indents.append(4)
                        self.line += 1
                        yield KeyMultiToken(
                            key=key,
                            value=value,
                            mark=key_mark,
                            value_mark=self.mark,
                        )
                        self.indents.pop()
                    self.line += len(lines)
                case _:
                    raise ValueError(f"{value}, {type(value)}")

    def handle_sequence(self, o: YAMLSequence) -> TokenGenerator:
        for value in o:
            match value:
                case dict():
                    yield SequenceBlockToken(mark=self.mark)
                    self.indents.append(2)
                    yield from self.handle_mapping(value)
                    self.indents.pop()
                case str():
                    sequence_mark = self.mark
                    lines = value.splitlines()
                    if len(lines) == 1:
                        yield SequenceValueToken(value=value, mark=sequence_mark)
                    else:
                        self.indents.append(4)
                        self.line += 1
                        yield SequenceMultiToken(value=value, mark=sequence_mark, value_mark=self.mark)
                        self.indents.pop()
                    self.line += len(lines)
                case _:
                    raise ValueError(f"{value}, {type(value)}")


def tokenize(o: YAMLCollection) -> TokenGenerator:
    yield from Tokenizer(o).tokenize()
