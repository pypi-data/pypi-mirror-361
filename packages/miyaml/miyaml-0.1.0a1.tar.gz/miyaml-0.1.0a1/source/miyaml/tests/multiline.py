# SPDX-License-Identifier: MIT
from pathlib import Path

from ..tokens import KeyMultiToken, Mark
from ..types import YAMLMapping

tokens = [
    KeyMultiToken(
        key="multiline_string",
        value="This is a multiline paragraph\nAnd this is the second paragraph.\n\nAnd a third paragraph.",
        mark=Mark(line=1, column=1),
        value_mark=Mark(line=2, column=5),
    ),
]

de: YAMLMapping = {
    "multiline_string": "This is a multiline paragraph\nAnd this is the second paragraph.\n\nAnd a third paragraph.",
}

se = Path(__file__).parent.joinpath("multiline.yaml")
