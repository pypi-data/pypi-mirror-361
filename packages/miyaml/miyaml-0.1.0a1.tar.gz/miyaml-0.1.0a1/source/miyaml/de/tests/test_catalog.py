# SPDX-License-Identifier: MIT
from ...tests import catalog
from ..parser import parse
from ..scanner import scan


def test_parser() -> None:
    with catalog.se.open(encoding="utf-8") as file:
        result = parse(scan(file))
    assert result
