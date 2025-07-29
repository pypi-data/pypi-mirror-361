
from __future__ import annotations

import typing

from scicheck import _message

if typing.TYPE_CHECKING:
    from typing import Any, Callable, Optional
    from scicheck.errors import NotTypeError, CannotConvertToType


def astuple(input: Any) -> tuple:
    if isinstance(input, tuple):
        return input
    elif isinstance(input, list):
        return tuple(input)
    else:
        return (input,)





def check_type(
    input: Any, 
    types: type | tuple[type], 
    name: str, 
    description: str | None,
    strict: bool,
    NotTypeError: Optional[NotTypeError] = None,
    CannotConvertToType: Optional[CannotConvertToType] = None,
):
    "Generalized type checker. Optionally allows type coercion"
    
    # Strict type checking
    types = astuple(types)
    if isinstance(input, types):
        return input
    elif strict:
        message = _message.not_type(name, types, description)
        raise NotTypeError(message)

    # Attempt type conversion
    converter = types[0]
    return convert(input, converter, name, description, CannotConvertToType)


def convert(
    input: Any, 
    converter: Callable, 
    name: str, 
    description: str, 
    CannotConvertToType: CannotConvertToType
) -> Any:
    "Attempts to convert an object to a specific type"

    try:
        return converter(input)
    except Exception as error:
        message = _message.cannot_convert(name, description)
        raise CannotConvertToType(message) from error

