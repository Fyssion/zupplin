from __future__ import annotations

import typing
from typing import Any, Literal, NotRequired, Required, Type, TypedDict


def get_required_keys(td: Type[TypedDict]) -> list[str]:
    required_keys: list[str] = []

    for k, v in typing.get_type_hints(td, include_extras=True).items():
        orig = typing.get_origin(v)
        if (td.__total__ or orig is Required) and orig is not NotRequired:  # double negative heh
            required_keys.append(k)

    return required_keys


def validate(td: Type[TypedDict], body: dict[str, Any]) -> bool:
    """Returns whether a body adheres to a validation TypedDict"""

    annotations = typing.get_type_hints(td)

    # TypedDict.__required_keys__ fails when __future__.annotations is imported
    # because ForwardRefs are not evaluated, and I can't think of a better fix
    if not all((k in body) for k in get_required_keys(td)):
        return False

    for k, v in body.items():
        if k not in annotations:
            return False

        v_type = annotations[k]
        orig_type = typing.get_origin(v_type)

        if orig_type is list:
            if not isinstance(v, list):
                return False

            if not all((isinstance(e, typing.get_args(v_type)[0]) for e in v)):
                return False

        elif orig_type is Literal:
            if v not in typing.get_args(v_type):
                return False

        # nested TypedDicts
        # TypedDict is a plain dict at runtime
        elif issubclass(v_type, dict):
            if not isinstance(v, dict):
                return False

            if not validate(v_type, v):  # type: ignore
                return False

        elif not isinstance(v, v_type):
            return False

    return True
