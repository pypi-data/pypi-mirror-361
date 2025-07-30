# SPDX-License-Identifier: MIT
from dataclasses import dataclass
from typing import Optional

from .tokens import Mark


@dataclass
class MarkedError(Exception):
    problem: str
    mark: Optional[Mark]

    def __str__(self) -> str:
        return f"{self.problem}\nOccured at: `{self.mark}`"
