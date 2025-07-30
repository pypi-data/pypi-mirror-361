# SPDX-License-Identifier: MIT
from io import StringIO

from ...tests import multiline
from ..serializer import serialize
from ..tokenizer import tokenize


def test_tokenizer() -> None:
    result = list(tokenize(multiline.de))

    expected = multiline.tokens
    assert result == expected


def test_serializer() -> None:
    stream = StringIO()
    serialize(stream, tokenize(multiline.de))
    result = stream.getvalue()

    expected = multiline.se.read_text(encoding="utf-8")
    assert result == expected
