# SPDX-License-Identifier: MIT
from pathlib import Path

from ..tokens import KeyValueToken, Mark
from ..types import YAMLMapping

tokens = [
    KeyValueToken(key="A", value="B", mark=Mark(line=1, column=1)),
]

de: YAMLMapping = {"A": "B"}

se = Path(__file__).parent.joinpath("singleline.yaml")
