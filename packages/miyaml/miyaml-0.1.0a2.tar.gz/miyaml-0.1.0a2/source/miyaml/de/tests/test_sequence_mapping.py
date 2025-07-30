# SPDX-License-Identifier: MIT
from ...tests import sequence_mapping
from ..parser import parse
from ..scanner import scan


def test_scanner() -> None:
    with sequence_mapping.se.open(encoding="utf-8") as file:
        result = list(scan(file))

    expected = sequence_mapping.tokens
    assert result == expected


def test_parser() -> None:
    with sequence_mapping.se.open(encoding="utf-8") as file:
        result = parse(scan(file))

    expected = sequence_mapping.de
    assert result == expected
