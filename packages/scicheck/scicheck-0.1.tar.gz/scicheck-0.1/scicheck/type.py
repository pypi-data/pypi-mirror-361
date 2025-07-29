from __future__ import annotations

import typing

from scicheck.errors import CannotConvertToString, NotStringError, NotTypeError
from scicheck.utils import check_type

if typing.TYPE_CHECKING:
    from typing import Any, Optional

# Alias for the built-in type object (whose name we will overshadow)
type_ = type


#####
# User Functions
#####


def type(
    input: Any,
    types: type_ | tuple[type_],
    name: str = "input",
    description: Optional[str] = None,
) -> Any:
    """
    Checks an input is a supported type and returns the input
    ----------
    type(input, types)
    Checks that an input is one of the supported types and returns the input. The
    `types` input may be a type, tuple of types, or a UnionType object. Raises an
    informative error if the input is not a supported type.

    Note: The `types` input should not include `None` as a supported type. To validate
    the type of an optional input, we recommend the following syntax:

        if input is not None:
            scicheck.type(input, ...)

    type(..., name)
    type(..., name, description)
    Customizes the error message for when the input fails the check. The error message
    will follow the form: "{name} must be a {description}". The `name` is the name of
    the input being validated and defaults to "input". The `description` provides a
    description of the supported types and defaults to the class names of the input
    types.
    ----------
    Inputs:
        input: The input being validated
        types: The allowed input types
        name: A name for the input being validated
        description: A description of the supported types

    Outputs:
        Any: The validated input

    Raises:
        TypeError: If the input is not one of the supported types
    """

    return check_type(
        input, types, name, description, strict=True, TypeError=NotTypeError
    )

def string(
    input: Any,
    name: str = "input",
    *,
    strict: bool = True,
) -> Any:
    """
    Checks an input is a string and returns the input
    ----------
    string(input)
    string(input, name)
    Checks an input is a string and returns the input if valid. Otherwise, uses an
    informative error. Use `name` to provide a name for the input being checked. The
    `name` defaults to "input" and is always placed at the beginning of the error
    message.
    ----------
    Inputs:
        input: The input being checked
        name: A name for the input

    Outputs:
        str: The validated string

    Raises:
        NotStringError: If the input is not a string
    """
    return check_type(
        input, 
        str, 
        name, 
        description='string',
        strict=strict, 
        NotTypeError=NotStringError, 
        CannotConvertToType=CannotConvertToString
    )


