


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

class NumericError(ScicheckError):
    "When a numeric input is not valid"

class NumericTypeError(NumericError, TypeError):
    "When an input does not represent a numeric type"

class NumericValueError(NumericError, ValueError):
    "When a numeric alue is not valid"


#####
# Not Type
#####

class NotNumericError(NumericTypeError, NotTypeError):
    "When an input is not an int, float, or complex"

class NotComplexError(NotNumericError):
    "When an input is not a complex"

class NotFloatError(NotNumericError):
    "When an input is not a float"

class NotIntError(NotNumericError):
    "When an input is not an int"

class NotRealError(NotNumericError):
    "When an input is not an int or float"


#####
# Cannot Convert
#####

class CannotConvertToNumeric(NumericTypeError, CannotConvertToType):
    "When an input cannot be converted to an int, float, or complex"

class CannotConvertToComplex(CannotConvertToNumeric):
    "When an input cannot be converted to a complex"

class CannotConvertToFloat(CannotConvertToNumeric):
    "When an input cannot be converted to a float"

class CannotConvertToInt(CannotConvertToNumeric):
    "When an input cannot be converted to an int"

class CannotConvertToReal(CannotConvertToNumeric):
    "When an input cannot be converted to an int or float"


#####
# Real-valued
#####

class RealValueError(NumericValueError):
    "When a real-valued number is not valid"

class IsNaNError(RealValueError):
    "When a real-valued number is NaN"

class IsInfError(RealValueError):
    "When a real-valued number is infinite"


#####
# Comparison
#####

class ComparisonError(RealValueError):
    "When a real-valued number fails a comparison check"

class NotLess(ComparisonError):
    "When a real-valued number is not less than a value"

class NotLessEqual(ComparisonError):
    "When a real-valued number is not less than or equal to a value"

class NotGreater(ComparisonError):
    "When a real-valued number is not greater than a value"

class NotGreaterEqual(ComparisonError):
    "When a real-valued number is not greater than or equal to a value"


#####
# Sign
#####

class SignError(ComparisonError):
    "When a real-valued number has the wrong sign"

class NotPositive(SignError, NotGreater):
    "When a real-valued number is not greater than zero"

class NotNegative(SignError, NotLess):
    "When a real-valud number is not less than zero"

class NotPositiveOrZero(SignError, NotGreaterEqual):
    "When a real-valued number is not >= 0"

class NotNegativeOrZero(SignError, NotLessEqual):
    "When a real-valued number is not <= 0"




