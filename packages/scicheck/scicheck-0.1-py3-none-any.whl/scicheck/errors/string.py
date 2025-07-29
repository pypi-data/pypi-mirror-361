
from scicheck.errors.base import (
    CannotConvertToType,
    NotTypeError,
    ScicheckError,
    TypeError,
    ValueError,
)

#####
# Bases
#####


class StringError(ScicheckError):
    "When a string input is not valid"

class StringTypeError(StringError, TypeError):
    "When an input does not represent a string"

class StringValueError(StringError, ValueError):
    "When a string is not valid"


#####
# Type
#####

class NotStringError(StringTypeError, NotTypeError):
    "When an input is not a string"

class CannotConvertToString(StringTypeError, CannotConvertToType):
    "When an input cannot be converted to a string"
