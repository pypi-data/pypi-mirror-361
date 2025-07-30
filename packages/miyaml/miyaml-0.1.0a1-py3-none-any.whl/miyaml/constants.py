# SPDX-License-Identifier: MIT
from enum import EnumType, StrEnum


class SYMBOL(StrEnum):
    KEY = ":"
    SEQUENCE = "-"
    COMMENT = "#"
    MULTI = "|"


class CHAR(EnumType):
    """https://docs.python.org/3/library/stdtypes.html#str.splitlines"""

    SPACE = " "
    TAB = "\t"
    WHITESPACE = (SPACE, TAB)
    LF = "\n"
    CR = "\r"
    CRLF = "\r\n"
    FF = "\f"
    FS = "\x1c"
    GS = "\x1d"
    RS = "\x1e"
    NL = "\x85"
    LS = "\u2028"
    PS = "\u2028"
    LINEBREAK = (LF, CR, CRLF, FF, FS, GS, RS, NL, LS, PS)
    NULL = "\0"
    END = (NULL, *LINEBREAK)
    SINGLEQUOTE = "'"
    DOUBLEQUOTE = '"'
    QUOTE = (SINGLEQUOTE, DOUBLEQUOTE)
    RESERVED = tuple((value.value for value in SYMBOL.__members__.values()))


class PATTERN(StrEnum):
    SEQUENCE = f"{SYMBOL.SEQUENCE}{CHAR.SPACE}"
    COMMENT = f"{CHAR.SPACE}{SYMBOL.COMMENT}"
    KEY = f"{SYMBOL.KEY}{CHAR.SPACE}"
    BLOCK = f"{SYMBOL.KEY}{CHAR.LF}"
    MULTI = f"{SYMBOL.MULTI}{CHAR.LF}"
