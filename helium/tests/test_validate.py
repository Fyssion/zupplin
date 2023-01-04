from typing import Literal, NotRequired, TypedDict

import pytest

from app.utils.validate import validate


class PlainDict(TypedDict):
    foo: str
    bar: int


class NotRequiredDict(TypedDict):
    foo: NotRequired[int]
    bar: int


class ListDict(TypedDict):
    foo: list[int]


class LiteralDict(TypedDict):
    foo: Literal[1, 2]


class SimpleDict(TypedDict):
    bar: int


class NestedDict(TypedDict):
    foo: SimpleDict


test_data = [
    (PlainDict, {'foo': 'baz', 'bar': 1}, True),
    (PlainDict, {'foo': 'baz', 'bar': 'baz'}, False),
    (PlainDict, {'foo': 'baz'}, False),
    (NotRequiredDict, {'foo': 1, 'bar': 1}, True),
    (NotRequiredDict, {'bar': 1}, True),
    (ListDict, {'foo': [1, 2, 3]}, True),
    (ListDict, {'foo': [1, 'b', 'c']}, False),
    (ListDict, {'foo': 'totally a list'}, False),
    (LiteralDict, {'foo': 1}, True),
    (LiteralDict, {'foo': 3}, False),
    (LiteralDict, {'foo': 'a'}, False),
    (NestedDict, {'foo': {'bar': 1}}, True),
    (NestedDict, {'foo': {'bar': 'a'}}, False),
    (NestedDict, {'foo': 'bar'}, False),
]

@pytest.mark.parametrize('td,d,expected', test_data)
def test_validate(td, d, expected):
    assert validate(td, d) == expected

