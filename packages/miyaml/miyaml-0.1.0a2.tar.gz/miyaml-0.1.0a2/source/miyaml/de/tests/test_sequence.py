# SPDX-License-Identifier: MIT
from ...tests import sequence
from ..parser import parse
from ..scanner import scan


def test_scanner() -> None:
    with sequence.se.open(encoding="utf-8") as file:
        result = list(scan(file))

    expected = sequence.tokens
    assert result == expected


def test_parser() -> None:
    with sequence.se.open(encoding="utf-8") as file:
        result = parse(scan(file))

    expected = sequence.de
    assert result == expected
