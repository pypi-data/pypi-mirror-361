# SPDX-License-Identifier: MIT
from __future__ import annotations

from dataclasses import dataclass, field
from types import NoneType
from typing import Optional


@dataclass(kw_only=True)
class Mark:
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Line: {self.line}, Column: {self.column}"


@dataclass(kw_only=True)
class TokenMixin:
    mark: Mark

    @property
    def indent(self) -> int:
        return self.mark.column - 1


@dataclass()
class KeyMixin(TokenMixin):
    key: str


@dataclass()
class ValueMixin(TokenMixin):
    value: str
    value_mark: Optional[Mark] = field(default_factory=NoneType)

    @property
    def value_indent(self) -> int:
        return self.value_mark.column - 1  # type: ignore


@dataclass
class KeyValueToken(ValueMixin, KeyMixin):
    pass


@dataclass
class KeyMultiToken(ValueMixin, KeyMixin):
    pass


@dataclass
class KeyBlockToken(KeyMixin):
    pass


@dataclass
class SequenceValueToken(ValueMixin):
    pass


@dataclass
class SequenceBlockToken(TokenMixin):
    pass


@dataclass
class SequenceMultiToken(ValueMixin):
    pass


type Token = (
    KeyValueToken | KeyMultiToken | KeyBlockToken | SequenceValueToken | SequenceMultiToken | SequenceBlockToken
)
