
from __future__ import annotations

import typing
from math import isinf, isnan

from scicheck.utils import convert
from scicheck import _message
from scicheck.errors import (
    CannotConvertToComplex,
    CannotConvertToFloat,
    CannotConvertToInt,
    CannotConvertToNumeric,
    CannotConvertToReal,
    IsInfError,
    IsNaNError,
    NotComplexError,
    NotFloatError,
    NotIntError,
    NotNumericError,
    NotRealError,
)

if typing.TYPE_CHECKING:
    from typing import Any
    Real = int | float
    Numeric = Real | complex


# Aliases for overshadowed built-in types
float_ = float
complex_ = complex



#####
# Utilities
#####

def _float_as_int(input: float_, name: str) -> int:
    "Converts a float to an int when possible"
    if input.is_integer():
        return int(input)
    else:
        raise CannotConvertToInt(f"{name} ({input}) is not an integer")
    

def _complex_as_float(input: complex_, name: str, description: str, error: Exception) -> float_:
    "Converts a complex to a float when possible"

    if input.imag == 0:
        return input.real
    else:
        value = f"({input})" if input.real==0 else input
        raise error(
            f"{name} {value} is complex-valued, so cannot be converted to {description}"
        )
    


def _not_numeric(name: str) -> NotNumericError:
    message = f"{name} must be a numeric type"
    return NotNumericError(message)





#####
# Type
#####







def numeric(input: Any, name: str = 'input', *, strict: bool = False) -> Numeric:
    "Checks that an input represents a numeric type"

    # Strict
    if isinstance(input, (int, float_, complex_)):
        return input
    elif strict:
        raise _not_numeric(name)
    
    # Attempt conversion
    input = convert(
        input, complex_, name, 'numeric type', CannotConvertToNumeric
    )

    # Simplify type as appropriate
    if input.imag == 0:
        input = input.real
    if input.is_integer():
        input = int(input)
    return input



def complex(
    input: Any, 
    name: str = 'input', 
    *, 
    strict: bool = False,
    numeric_only: bool = True
) -> complex_:

    # Strict
    if isinstance(input, complex_):
        return input
    elif strict:
        raise NotComplexError(_message.not_type(name, 'complex'))
    
    # Convert other numeric types
    elif isinstance(input, (int, float_)):
        return complex_(input)
    
    # Require numeric or attempt type conversion
    elif numeric_only:
        raise _not_numeric(name)
    else:
        return convert(input, complex_, name, 'complex', CannotConvertToComplex)



def float(
    input: Any, 
    name: str = 'input', 
    *, 
    strict: bool = False,
    numeric_only: bool = True,
) -> float_:

    # Strict
    if isinstance(input, float_):
        return input
    elif strict:
        raise NotFloatError(_message.not_type(name, 'float'))
    
    # Handle complex and int types
    elif isinstance(input, complex_):
        return _complex_as_float(input, name, 'a float', CannotConvertToFloat)
    elif isinstance(input, int):
        return float_(input)
    
    # Require numeric, or attempt type conversion
    elif numeric_only:
        raise _not_numeric(name)
    else:
        return convert(input, float_, name, 'a float', CannotConvertToFloat)
    



def integer(
    input: Any, 
    name: str = 'input', 
    *, 
    strict: bool = False,
    numeric_only: bool = True,
) -> int:

    # Strict
    if isinstance(input, int):
        return input
    elif strict:
        raise NotIntError(f"{name} must be an int")
    
    # Handle float and complex
    if isinstance(input, complex_):
        input = _complex_as_float(input, name, 'an integer', CannotConvertToInt)
    if isinstance(input, float_):
        return _float_as_int(input, name)
    
    # Require numeric or attempt type conversion
    elif numeric_only:
        raise _not_numeric(name)
    else:
        return convert(input, int, name, 'an integer', CannotConvertToInt)
    
    

def real(
    input: Any, 
    name: str = 'input', 
    *, 
    strict: bool = False,
    numeric_only: bool = True,
    allow_nan: bool = False,
    allow_inf: bool = False, 
) -> Real:
    
    # Strict
    if isinstance(input, int):
        return input
    elif strict and not isinstance(input, float_):
        raise NotRealError(f"{name} must be an int or float")
    
    # Handle complex
    elif isinstance(input, complex_):
        input = _complex_as_float(input, name, )
    
    # Require numeric or attempt type conversion
    elif numeric_only:
        raise _not_numeric(name)
    else:
        input = convert(
            input, float_, name, 'a real-valued number', CannotConvertToReal
        )

    # Optionally prevent NaN and Inf
    if isnan(input) and not allow_nan:
        raise IsNaNError(f"{name} cannot be NaN")
    elif isinf(input) and not allow_inf:
        raise IsInfError(f"{name} cannot be Inf")
    return input


# #####
# # Comparison operators
# #####

# def _operator(op: Callable):
#     "Returns the description and error associated with different operators"

#     if op == lt:
#         return 'less than', NotLess
#     elif op == le:
#         return 'less than or equal to', NotLessEqual
#     elif op == gt:
#         return 'greater than', NotGreater
#     elif op == ge:
#         return 'greater than or equal to', NotGreaterEqual



# def _compare(input: Real, op: Callable, X: Real, name: str) -> None:

#     if not op(input, X):
#         description, error = _operator(op)
#         raise error(input, description, X, name)


# def less(input: Real, X: Real, name: str = 'input') -> None:
#     _compare(input, lt, X, name)
    
# def less_equal(input: Real, X: Real, name: str = 'input') -> None:
#     _compare(input, le, X, name)

# def greater(input: Real, X: Real, name: str = 'input') -> None:
#     _compare(input, gt, X, name)

# def greater_equal(input: Real, X: Real, name: str = 'input') -> None:
#     _compare(input, ge, X, name)



# #####
# # Inclusive/Exclusive Ranges
# #####

# def in_range(
#     input: Real, 
#     min: Real, 
#     max: Real,
#     name: str = 'input',
#     *, 
#     include_min: bool = True, 
#     include_max: bool = True,
# ) -> None:
    
#     # Get the operators for each bound
#     bounds = (
#         (min, include_min, ge, gt),
#         (max, include_max, le, lt),
#     )

#     # Compare to each bound. Skip any unprovided bounds
#     for bound, use_inclusive, inclusive, exclusive in bounds:
#         op = inclusive if use_inclusive else exclusive
#         _compare(input, op, bound, name)


# def _sign(
#     input: Real, 
#     name: str, 
#     allow_zero: bool, 
#     inclusive: Callable, 
#     exclusive: Callable, 
#     error: Exception
# ):

#     op = inclusive if allow_zero else exclusive
#     if not op(input, 0):
#         description, _ = _operator(op)
#         raise error(input, description, 0, name)


# def positive(input: Real, name: str = 'input', *, allow_zero: bool = False):
#     _sign(input, name, allow_zero, inclusive=ge, exclusive=gt, error=NotPositiveError)

# def negative(input: Real, name: str = 'input', *, allow_zero: bool = False):
#     _sign(input, name, allow_zero, inclusive=le, exclusive=lt, error=NotNegativeError)


 
