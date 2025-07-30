# SPDX-License-Identifier: MIT
from ...tests import singleline
from ..parser import parse
from ..scanner import scan


def test_scanner() -> None:
    with singleline.se.open(encoding="utf-8") as file:
        result = list(scan(file))

    expected = singleline.tokens
    assert result == expected


def test_parser() -> None:
    with singleline.se.open(encoding="utf-8") as file:
        result = parse(scan(file))

    expected = singleline.de
    assert result == expected
