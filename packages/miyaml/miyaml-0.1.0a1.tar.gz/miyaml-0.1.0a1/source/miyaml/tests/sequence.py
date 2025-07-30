# SPDX-License-Identifier: MIT
from pathlib import Path

from ..tokens import Mark, SequenceMultiToken, SequenceValueToken
from ..types import YAMLSequence

tokens = [
    SequenceValueToken(mark=Mark(line=1, column=1), value="One"),
    SequenceValueToken(mark=Mark(line=2, column=1), value="Two"),
    SequenceValueToken(mark=Mark(line=3, column=1), value="Three"),
    SequenceValueToken(mark=Mark(line=4, column=1), value="Four"),
    SequenceMultiToken(mark=Mark(line=5, column=1), value="Five.A\n\nFive.B", value_mark=Mark(line=6, column=5)),
]

de: YAMLSequence = ["One", "Two", "Three", "Four", "Five.A\n\nFive.B"]

se = Path(__file__).parent.joinpath("sequence.yaml")
