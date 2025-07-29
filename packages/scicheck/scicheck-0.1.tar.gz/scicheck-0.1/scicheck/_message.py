


def strlist(strings: list[str]) -> str:
    "Returns a nicely formatted string list"

    if len(strings) == 1:
        return strings[0]
    elif len(strings) == 2:
        return f"{strings[0]} or {strings[1]}"
    else:
        head = ", ".join(strings[:-1])
        return ", or ".join([head, strings[-1]])


def message(name: str, info: str) -> str:
    return f"{name} {info}"

def _description(description: str) -> str:
    if not description.startswith(('a ', 'an ')):
        description = f"a {description}"
    return description

def cannot_convert(name: str, description: str) -> str:
    description = _description(description)
    return f"{name} cannot be converted to {description}"

def not_type(name: str, types: tuple[type], description: str) -> str:
    if description is None:
        description = strlist([type.__name__ for type in types])
    description = _description(description)
    return f"{name} must be {description}"


def _path(path, message):
    return f"{message}\nPath: {path}"


def wrong_path(name, path, type):
    message = f"{name} does not point to a {type}"
    return _path(path, message)

def missing(name, path):
    message = f"{name} does not exist"
    return _path(path, message)

def exists(name, path):
    message = f"{name} already exists"
    return _path(path, message)

def not_empty(name, path):
    message = f"{name} is a folder, but the folder is not empty"
    return _path(path, message)
    

