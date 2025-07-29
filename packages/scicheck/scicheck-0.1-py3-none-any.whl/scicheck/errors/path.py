

from scicheck.errors.base import (
    CannotConvertToType,
    NotTypeError,
    ScicheckError,
    TypeError,
    ValueError,
)

#####
# Base
#####

class PathError(ScicheckError):
    "When a path input is not valid"

class PathTypeError(PathError, TypeError):
    "When an input does not represent a path"

class PathValueError(PathError, ValueError):
    "When a path is not valid"
    def __init__(self, message, path):
        message = f"{message}\nPath: {path}"
        super().__init__(message)


#####
# Type
#####

class NotPathError(PathTypeError, NotTypeError):
    "When an input is not a pathlib.Path object"


class CannotConvertToPath(PathTypeError, CannotConvertToType):
    "When an input cannot be converted to a pathlib.Path object"


#####
# Existence
#####

class PathNotFoundError(PathValueError, FileNotFoundError):
    "When a path does not exist"

class PathExistsError(PathValueError, FileExistsError):
    "When a path already exists"



#####
# File
#####

class FilePathError(PathValueError):
    "When a path does not point to a valid file"


class FileNotFoundError(FilePathError, PathNotFoundError):
    "When a file does not exist"


class FileExistsError(FilePathError, PathExistsError):
    "When a file already exists"


class NotFileError(FilePathError):
    "When a path points to a resource that is not a file"


#####
# Folder
#####

class FolderPathError(PathValueError):
    "When a path does not point to a valid folder"

class FolderNotFoundError(FolderPathError, PathNotFoundError):
    "When a folder does not exist"

class FolderExistsError(FolderPathError, PathExistsError):
    "When a folder already exists"

class NotFolderError(FolderPathError, NotADirectoryError):
    "When a path points to a resource that is not a folder"

class FolderNotEmpty(FolderPathError):
    "When a path points to a non-empty folder"