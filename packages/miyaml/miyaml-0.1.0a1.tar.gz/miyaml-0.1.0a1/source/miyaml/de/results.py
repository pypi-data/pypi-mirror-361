# SPDX-License-Identifier: MIT
from enum import Enum, auto


class ReaderResult(Enum):
    CONTINUE = auto()
    END = auto()


class LiteralResult(Enum):
    KEY = auto()
    VALUE = auto()
    COMMENT = auto()
    BLOCK = auto()
    MULTI = auto()
