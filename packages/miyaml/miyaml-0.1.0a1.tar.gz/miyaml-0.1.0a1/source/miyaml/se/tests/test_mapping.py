# SPDX-License-Identifier: MIT
from io import StringIO

from ...tests import mapping
from ..serializer import serialize
from ..tokenizer import tokenize


def test_tokenizer() -> None:
    result = list(tokenize(mapping.de))

    expected = mapping.tokens
    assert result == expected


def test_serializer() -> None:
    stream = StringIO()
    serialize(stream, tokenize(mapping.de))
    result = stream.getvalue()

    expected = mapping.se.read_text(encoding="utf-8")
    assert result == expected
