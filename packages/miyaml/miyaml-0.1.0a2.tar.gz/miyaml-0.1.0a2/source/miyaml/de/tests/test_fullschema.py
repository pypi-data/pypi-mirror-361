# SPDX-License-Identifier: MIT
from ...tests import fullschema
from ..parser import parse
from ..scanner import scan


def test_scanner() -> None:
    with fullschema.se.open(encoding="utf-8") as file:
        result = list(scan(file))

    expected = fullschema.tokens
    assert result == expected


def test_parser() -> None:
    with fullschema.se.open(encoding="utf-8") as file:
        result = parse(scan(file))

    expected = fullschema.de
    assert result == expected
