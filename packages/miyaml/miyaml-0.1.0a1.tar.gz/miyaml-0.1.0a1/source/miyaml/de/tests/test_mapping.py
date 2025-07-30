# SPDX-License-Identifier: MIT
from ...tests import mapping
from ..parser import parse
from ..scanner import scan


def test_scanner() -> None:
    with mapping.se.open(encoding="utf-8") as file:
        result = list(scan(file))

    expected = mapping.tokens
    assert result == expected


def test_parser() -> None:
    with mapping.se.open(encoding="utf-8") as file:
        result = parse(scan(file))

    expected = mapping.de
    assert result == expected
