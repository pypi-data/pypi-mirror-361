# SPDX-License-Identifier: MIT
from ...tests import multiline
from ..parser import parse
from ..scanner import scan


def test_scanner() -> None:
    with multiline.se.open(encoding="utf-8") as file:
        result = list(scan(file))

    expected = multiline.tokens
    assert result == expected


def test_parser() -> None:
    with multiline.se.open(encoding="utf-8") as file:
        result = parse(scan(file))

    expected = multiline.de
    assert result == expected
