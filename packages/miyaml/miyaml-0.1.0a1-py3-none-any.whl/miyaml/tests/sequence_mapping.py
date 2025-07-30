# SPDX-License-Identifier: MIT
from pathlib import Path

from ..tokens import KeyBlockToken, KeyValueToken, Mark, SequenceBlockToken, SequenceValueToken
from ..types import YAMLSequence

tokens = [
    SequenceBlockToken(mark=Mark(line=1, column=1)),
    KeyBlockToken(key="map1A", mark=Mark(line=1, column=3)),
    SequenceValueToken(value="A", mark=Mark(line=2, column=7)),
    SequenceValueToken(value="AA", mark=Mark(line=3, column=7)),
    KeyValueToken(key="map1B", value="B", mark=Mark(line=4, column=3)),
    SequenceBlockToken(mark=Mark(line=5, column=1)),
    KeyBlockToken(key="map2", mark=Mark(line=5, column=3)),
    SequenceValueToken(value="1", mark=Mark(line=6, column=7)),
    SequenceValueToken(value="2", mark=Mark(line=7, column=7)),
]

de: YAMLSequence = [
    {
        "map1A": [
            "A",
            "AA",
        ],
        "map1B": "B",
    },
    {
        "map2": [
            "1",
            "2",
        ],
    },
]

se = Path(__file__).parent.joinpath("sequence_mapping.yaml")
