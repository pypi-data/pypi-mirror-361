# SPDX-License-Identifier: MIT
from typing import Generator

from .tokens import Token

type YAMLMapping = dict[str, YAMLObject]
type YAMLSequence = list[YAMLObject]
type YAMLCollection = YAMLMapping | YAMLSequence
type YAMLObject = YAMLCollection | str
type TokenGenerator = Generator[Token, None, None]
