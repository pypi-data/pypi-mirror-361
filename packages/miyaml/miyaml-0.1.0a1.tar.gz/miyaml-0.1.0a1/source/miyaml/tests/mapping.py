# SPDX-License-Identifier: MIT
from pathlib import Path

from ..tokens import KeyBlockToken, KeyValueToken, Mark
from ..types import YAMLMapping

tokens = [
    KeyValueToken(key="name", value="Kazuo Shinohara", mark=Mark(line=1, column=1)),
    KeyValueToken(key="based", value="japan.tokyo", mark=Mark(line=2, column=1)),
    KeyBlockToken(key="projects", mark=Mark(line=3, column=1)),
    KeyBlockToken(key="house-of-white", mark=Mark(line=4, column=5)),
    KeyValueToken(key="year", value="1966", mark=Mark(line=5, column=9)),
    KeyValueToken(key="born", value="1925", mark=Mark(line=6, column=1)),
]

de: YAMLMapping = {
    "name": "Kazuo Shinohara",
    "based": "japan.tokyo",
    "projects": {
        "house-of-white": {
            "year": "1966",
        },
    },
    "born": "1925",
}

se = Path(__file__).parent.joinpath("mapping.yaml")
