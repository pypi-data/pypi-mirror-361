# SPDX-License-Identifier: MIT
from dataclasses import dataclass, field
from typing import Any

from ..errors import MarkedError
from ..tokens import (
    KeyBlockToken,
    KeyMultiToken,
    KeyValueToken,
    SequenceBlockToken,
    SequenceMultiToken,
    SequenceValueToken,
)
from ..types import TokenGenerator, YAMLCollection


class ParserError(MarkedError):
    pass


@dataclass
class Parser:
    tokens: TokenGenerator
    collections: dict[int, YAMLCollection] = field(default_factory=dict)

    def parse(self) -> YAMLCollection:
        try:
            first = next(self.tokens)
        except StopIteration:
            return {}

        if first.indent != 0:
            raise ParserError(f"First token's indentation is `{first.indent}` and not `0`", first.mark)

        match first:
            case KeyValueToken() | KeyMultiToken():
                mapping: dict[Any, Any] = {}
                mapping[first.key] = first.value
                self.collections[first.indent] = mapping
            case KeyBlockToken():
                mapping = {}
                mapping[first.key] = {}
                self.collections[first.indent] = mapping
            case SequenceValueToken() | SequenceMultiToken():
                sequence: list[Any] = []
                sequence.append(first.value)
                self.collections[first.indent] = sequence
            case SequenceBlockToken():
                sequence = []
                self.collections[first.indent] = sequence
            case _:
                raise NotImplementedError(f"Missing implementation for {type(first)}")

        for token in self.tokens:
            parent: YAMLCollection
            match token:
                case KeyValueToken() | KeyMultiToken():
                    parent = self.get_collection(token.indent, dict)
                    parent[token.key] = token.value
                case KeyBlockToken():
                    parent = self.get_collection(token.indent, dict)
                    parent[token.key] = {}
                case SequenceValueToken() | SequenceMultiToken():
                    parent = self.get_collection(token.indent, list)
                    parent.append(token.value)
                case SequenceBlockToken():
                    parent = self.get_collection(token.indent, list)
                case _:
                    raise NotImplementedError(f"Missing implementation for {type(token)}")

        self.close_collections(first.indent)
        return self.collections[first.indent]

    def get_collection[T: YAMLCollection](self, target_indent: int, typ: type[T]):
        self.close_collections(target_indent)

        if target_indent in self.collections:
            collection = self.collections[target_indent]

            if not isinstance(collection, typ):
                raise TypeError(f"Expected `{typ}`, but got `{type(collection)}`")
        else:
            collection = typ()
            self.collections[target_indent] = collection

        return collection  # type: ignore

    def close_collections(self, target_indent: int) -> None:
        indents: list[int] = sorted(self.collections.keys())
        while indents:
            indent: int = indents.pop()
            if indent > target_indent:
                collection = self.collections.pop(indent)
                parent = self.collections[indents[-1]]

                match parent:
                    case dict():
                        parent[list(parent.keys())[-1]] = collection
                    case list():
                        if not isinstance(collection, dict):
                            raise TypeError(f"Expected `{dict}`, but got `{type(collection)}`")
                        else:
                            parent.append(collection)
                    case _:
                        raise TypeError(f"Expected {list} or {dict}, but got `{type(parent)}`")
            else:
                break


def parse(tokens: TokenGenerator) -> YAMLCollection:
    return Parser(tokens).parse()
