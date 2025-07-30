# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass
from typing import IO

from ..constants import CHAR, PATTERN, SYMBOL
from ..tokens import Mark
from .results import LiteralResult


@dataclass
class Reader:
    stream: IO[str]
    done: bool = False

    buffer: str = ""
    line: int = 0
    column: int = 0

    @property
    def indent(self) -> int:
        return self.column - 1

    @property
    def mark(self) -> Mark:
        return Mark(line=self.line, column=self.column)

    def readline(self) -> bool:
        self.buffer = self.stream.readline()

        self.line += 1
        self.column = 1

        if len(self.buffer) == 0:
            return False
        else:
            return True

    def advance(self, index: int = 1) -> None:
        self.column += index
        self.buffer = self.buffer[index:]

    def chomp_whitespace(self) -> None:
        before = len(self.buffer)
        self.buffer = self.buffer.lstrip()
        self.column += before - len(self.buffer)

    def get_literal(self) -> tuple[str, Mark, LiteralResult]:
        self.chomp_whitespace()
        mark = self.mark
        buffer = self.buffer

        if buffer.startswith(SYMBOL.COMMENT):
            return "", mark, LiteralResult.COMMENT

        if buffer.startswith(PATTERN.MULTI):
            return "", mark, LiteralResult.MULTI

        quoted: str
        if buffer.startswith(CHAR.QUOTE):
            quoted = buffer[0]
            buffer = buffer[1:]
        else:
            quoted = ""

        reason: LiteralResult
        chunks: str = ""
        skipped: int = 0
        while buffer:
            if buffer.startswith(CHAR.LINEBREAK):
                skipped += 1
                reason = LiteralResult.VALUE
                break
            elif quoted and buffer.startswith(quoted):
                skipped += 1
                reason = LiteralResult.VALUE
                break
            elif buffer.startswith(PATTERN.KEY):
                skipped += len(PATTERN.KEY)
                reason = LiteralResult.KEY
                break
            elif buffer.startswith(PATTERN.BLOCK):
                skipped += len(PATTERN.BLOCK)
                reason = LiteralResult.BLOCK
                break
            elif buffer.startswith(PATTERN.COMMENT):
                skipped += len(PATTERN.COMMENT)
                reason = LiteralResult.COMMENT
                break
            else:
                chunks += buffer[0]
                buffer = buffer[1:]
                continue
        else:
            reason = LiteralResult.VALUE

        self.advance(len(chunks) + skipped)
        return chunks, mark, reason
