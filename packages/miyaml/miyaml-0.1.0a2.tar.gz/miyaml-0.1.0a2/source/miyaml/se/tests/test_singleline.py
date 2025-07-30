# SPDX-License-Identifier: MIT
from io import StringIO

from ...tests import singleline
from ..serializer import serialize
from ..tokenizer import tokenize


def test_tokenizer() -> None:
    result = list(tokenize(singleline.de))

    expected = singleline.tokens
    assert result == expected


def test_serializer() -> None:
    stream = StringIO()
    serialize(stream, tokenize(singleline.de))
    result = stream.getvalue()

    expected = singleline.se.read_text(encoding="utf-8")
    assert result == expected
