# SPDX-License-Identifier: MIT
from typing import IO
from ..types import TokenGenerator
from ..constants import CHAR, PATTERN
from ..tokens import (
    KeyBlockToken,
    KeyMultiToken,
    KeyValueToken,
    SequenceBlockToken,
    SequenceMultiToken,
    SequenceValueToken,
)


def serialize(stream: IO[str], tokens: TokenGenerator) -> None:
    for token in tokens:
        stream.write(token.indent * CHAR.SPACE)
        match token:
            case KeyValueToken():
                stream.write(token.key + PATTERN.KEY + token.value + CHAR.LF)
            case KeyMultiToken():
                stream.write(token.key + PATTERN.KEY + PATTERN.MULTI)

                for line in token.value.splitlines():
                    if len(line) == 0:
                        stream.write(CHAR.LF)
                    else:
                        stream.write(token.value_indent * CHAR.SPACE + line + CHAR.LF)
            case KeyBlockToken():
                stream.write(token.key + PATTERN.BLOCK)
            case SequenceValueToken():
                stream.write(PATTERN.SEQUENCE + token.value + CHAR.LF)
            case SequenceMultiToken():
                stream.write(PATTERN.SEQUENCE + PATTERN.MULTI)

                for line in token.value.splitlines():
                    if len(line) == 0:
                        stream.write(CHAR.LF)
                    else:
                        stream.write(token.value_indent * CHAR.SPACE + line + CHAR.LF)
            case SequenceBlockToken():
                stream.write(PATTERN.SEQUENCE)

                token = next(tokens)
                match token:
                    case KeyValueToken():
                        stream.write(token.key + PATTERN.KEY + token.value + CHAR.LF)
                    case KeyBlockToken():
                        stream.write(token.key + PATTERN.BLOCK)
                    case _:
                        raise TypeError(f"Expected `{KeyValueToken | KeyBlockToken}` but got `{type(token)}`")
            case _:
                raise NotImplementedError(f"Missing implementation for {type(token)}")
