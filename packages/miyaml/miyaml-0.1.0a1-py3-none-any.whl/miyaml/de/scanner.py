# SPDX-License-Identifier: MIT
from __future__ import annotations
from typing import IO, Optional

from ..types import TokenGenerator
from ..errors import MarkedError
from .reader import Reader
from .results import LiteralResult
from ..tokens import (
    KeyBlockToken,
    KeyMultiToken,
    KeyValueToken,
    SequenceBlockToken,
    SequenceMultiToken,
    SequenceValueToken,
)
from ..constants import CHAR, PATTERN, SYMBOL


class ScannerError(MarkedError):
    pass


class Scanner:
    scanner: Scanner

    def __init__(self, stream: IO[str]):
        self.reader = Reader(stream)

    def scan(self) -> TokenGenerator:
        multi: Optional[KeyMultiToken | SequenceMultiToken] = None

        while True:
            if not self.reader.readline():
                if multi is not None:
                    multi.value = multi.value.rstrip(CHAR.LF)
                    yield multi
                break

            # Indent
            self.reader.chomp_whitespace()

            if multi is not None:
                # NOTE: Check if multline is initialized
                if multi.value_mark is None:
                    multi.value_mark = self.reader.mark

                if self.reader.indent < multi.value_indent and len(self.reader.buffer) > 0:
                    multi.value = multi.value.rstrip(CHAR.LF)
                    yield multi
                    multi = None
                else:
                    value, _, result = self.reader.get_literal()
                    multi.value += value + CHAR.LF
                    continue

            # Parse
            buffer = self.reader.buffer
            if len(self.reader.buffer) == 0:
                pass
            elif buffer.startswith(SYMBOL.COMMENT):
                # NOTE: No need to consume since we proceed to next line
                pass
            elif buffer.startswith(CHAR.LINEBREAK):
                # NOTE: No need to consume since we proceed to next line
                value, value_mark, result = self.reader.get_literal()
            elif buffer.startswith(PATTERN.SEQUENCE):
                sequence_mark = self.reader.mark
                self.reader.advance(len(PATTERN.SEQUENCE))

                value, value_mark, result = self.reader.get_literal()
                match result:
                    case LiteralResult.VALUE | LiteralResult.COMMENT:
                        yield SequenceValueToken(value, mark=sequence_mark)
                    case LiteralResult.MULTI:
                        multi = SequenceMultiToken("", mark=sequence_mark, value_mark=None)
                    case LiteralResult.BLOCK:
                        yield SequenceBlockToken(mark=sequence_mark)
                        yield KeyBlockToken(value, mark=value_mark)
                    case LiteralResult.KEY:
                        yield SequenceBlockToken(mark=sequence_mark)

                        key, key_mark = value, value_mark
                        value, value_mark, result = self.reader.get_literal()
                        match result:
                            case LiteralResult.VALUE | LiteralResult.COMMENT:
                                yield KeyValueToken(key, value, mark=key_mark)
                            case LiteralResult.KEY | LiteralResult.BLOCK:
                                raise ScannerError("Expected a value, got a key.", value_mark)
                            case LiteralResult.MULTI:
                                multi = KeyMultiToken(key, "", mark=key_mark, value_mark=None)
            else:
                key, key_mark, result = self.reader.get_literal()
                match result:
                    case LiteralResult.KEY:
                        value, mark, result = self.reader.get_literal()
                        match result:
                            case LiteralResult.VALUE | LiteralResult.COMMENT:
                                yield KeyValueToken(key, value, mark=key_mark)
                            case LiteralResult.MULTI:
                                multi = KeyMultiToken(key, "", mark=key_mark, value_mark=None)
                            case LiteralResult.KEY:
                                raise ScannerError("Nested mappings are not allowed on the same line.", mark)
                            case LiteralResult.BLOCK:
                                raise ScannerError("Nested mappings are not allowed on the same line.", mark)
                    case LiteralResult.BLOCK:
                        yield KeyBlockToken(key, mark=key_mark)
                    case LiteralResult.COMMENT:
                        raise ScannerError("Expected a key, got a comment instead", key_mark)
                    case LiteralResult.VALUE:
                        raise ScannerError("Expected a key, got a value.", key_mark)
                    case LiteralResult.MULTI:
                        raise ScannerError("Expected a key, got a multiline literal.", key_mark)


def scan(stream: IO[str]) -> TokenGenerator:
    return Scanner(stream).scan()
