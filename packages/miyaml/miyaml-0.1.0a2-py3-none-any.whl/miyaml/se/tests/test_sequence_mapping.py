# SPDX-License-Identifier: MIT
from io import StringIO

from ...tests import sequence_mapping
from ..serializer import serialize
from ..tokenizer import tokenize


def test_tokenizer() -> None:
    result = list(tokenize(sequence_mapping.de))

    expected = sequence_mapping.tokens
    assert result == expected


def test_serializer() -> None:
    stream = StringIO()
    serialize(stream, tokenize(sequence_mapping.de))
    result = stream.getvalue()

    expected = sequence_mapping.se.read_text(encoding="utf-8")
    assert result == expected
