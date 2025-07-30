# SPDX-License-Identifier: MIT
from io import StringIO

from ...tests import sequence
from ..serializer import serialize
from ..tokenizer import tokenize


def test_tokenizer() -> None:
    result = list(tokenize(sequence.de))

    expected = sequence.tokens
    assert result == expected


def test_serializer() -> None:
    stream = StringIO()
    serialize(stream, tokenize(sequence.de))
    result = stream.getvalue()

    expected = sequence.se.read_text(encoding="utf-8")
    assert result == expected
