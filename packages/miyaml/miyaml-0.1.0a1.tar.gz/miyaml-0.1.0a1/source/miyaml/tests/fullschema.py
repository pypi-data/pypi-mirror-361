# SPDX-License-Identifier: MIT
from pathlib import Path

from ..tokens import KeyBlockToken, KeyMultiToken, KeyValueToken, Mark, SequenceBlockToken, SequenceValueToken
from ..types import YAMLMapping

tokens = [
    KeyValueToken(mark=Mark(line=1, column=1), key="simple_map", value="SimpleKey"),
    KeyBlockToken(mark=Mark(line=2, column=1), key="nested_map"),
    KeyValueToken(mark=Mark(line=3, column=5), key="number", value="123"),
    KeyValueToken(mark=Mark(line=4, column=5), key="squoted", value="Quote"),
    KeyValueToken(mark=Mark(line=5, column=5), key="dquoted", value="QuoteQuote"),
    KeyBlockToken(mark=Mark(line=6, column=1), key="empty_key"),
    KeyBlockToken(mark=Mark(line=7, column=1), key="sequence"),
    SequenceValueToken(mark=Mark(line=8, column=5), value="Item1"),
    SequenceValueToken(mark=Mark(line=9, column=5), value="Item2"),
    KeyBlockToken(mark=Mark(line=10, column=1), key="seq_in_map"),
    KeyBlockToken(mark=Mark(line=11, column=5), key="seq1"),
    SequenceValueToken(mark=Mark(line=12, column=9), value="One"),
    SequenceValueToken(mark=Mark(line=13, column=9), value="Two"),
    KeyBlockToken(mark=Mark(line=14, column=5), key="seq2"),
    SequenceValueToken(mark=Mark(line=15, column=9), value="OneOne"),
    SequenceValueToken(mark=Mark(line=16, column=9), value="TwoTwo"),
    KeyBlockToken(mark=Mark(line=17, column=1), key="map_in_seq"),
    SequenceBlockToken(mark=Mark(line=18, column=5)),
    KeyBlockToken(mark=Mark(line=18, column=7), key="map1A"),
    SequenceValueToken(mark=Mark(line=19, column=11), value="A"),
    SequenceValueToken(mark=Mark(line=20, column=11), value="AA"),
    KeyValueToken(mark=Mark(line=21, column=7), key="map1B", value="B"),
    SequenceBlockToken(mark=Mark(line=22, column=5)),
    KeyBlockToken(mark=Mark(line=22, column=7), key="map2"),
    SequenceValueToken(mark=Mark(line=23, column=11), value="1"),
    SequenceValueToken(mark=Mark(line=24, column=11), value="2"),
    KeyBlockToken(mark=Mark(line=25, column=1), key="simple_in_seq"),
    SequenceBlockToken(mark=Mark(line=26, column=5)),
    KeyValueToken(mark=Mark(line=26, column=7), key="One", value="1"),
    SequenceBlockToken(mark=Mark(line=27, column=5)),
    KeyValueToken(mark=Mark(line=27, column=7), key="Two", value="2"),
    KeyMultiToken(
        mark=Mark(line=28, column=1),
        key="multiline_string",
        value="This is a multiline paragraph\nAnd this is the second paragraph.",
        value_mark=Mark(line=29, column=5),
    ),
    KeyBlockToken(mark=Mark(line=31, column=1), key="closing_key"),
]

de: YAMLMapping = {
    "simple_map": "SimpleKey",
    "nested_map": {
        "number": "123",
        "squoted": "Quote",
        "dquoted": "QuoteQuote",
    },
    "empty_key": {},
    "sequence": [
        "Item1",
        "Item2",
    ],
    "seq_in_map": {
        "seq1": [
            "One",
            "Two",
        ],
        "seq2": [
            "OneOne",
            "TwoTwo",
        ],
    },
    "map_in_seq": [
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
    ],
    "simple_in_seq": [
        {"One": "1"},
        {"Two": "2"},
    ],
    "multiline_string": "This is a multiline paragraph\nAnd this is the second paragraph.",
    "closing_key": {},
}

se = Path(__file__).parent.joinpath("fullschema.yaml")
