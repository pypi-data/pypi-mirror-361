# SPDX-License-Identifier: MIT
from io import StringIO

from ..__main__ import from_stream, to_stream
from ..types import YAMLMapping
from . import catalog

catalog_dict: YAMLMapping = {}


def test_from_stream() -> None:
    with catalog.se.open(encoding="utf-8") as file:
        result = from_stream(file, expect=dict)

    global catalog_dict
    catalog_dict = result
    assert result


def test_to_stream() -> None:
    stream = StringIO()

    to_stream(stream, catalog_dict)
