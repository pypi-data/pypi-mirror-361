

# Aliases for overshadowed exceptions
TypeError_ = TypeError
ValueError_ = ValueError


#####
# Bases
#####


class ScicheckError(Exception):
    "Errors originating from scicheck input validation"


class TypeError(ScicheckError, TypeError_):
    "When an input does not represent a supported type"
        

class ValueError(ScicheckError, ValueError_):
    "When an input represents the correct type, but has an unsupported value"


#####
# Type Bases
#####

class NotTypeError(TypeError):
    "When an input is not a required type"

           

class CannotConvertToType(TypeError):
    "When an input cannot be converted to a required type"
