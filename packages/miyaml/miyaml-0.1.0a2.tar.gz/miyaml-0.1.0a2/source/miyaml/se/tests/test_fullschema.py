# SPDX-License-Identifier: MIT
from io import StringIO

from ...tests import fullschema
from ..serializer import serialize
from ..tokenizer import tokenize


def test_tokenizer() -> None:
    result = list(tokenize(fullschema.de))

    expected = fullschema.tokens
    assert result == expected


def test_serializer() -> None:
    stream = StringIO()
    serialize(stream, tokenize(fullschema.de))
    result = stream.getvalue()

    assert result
