
from __future__ import annotations

import typing
from pathlib import Path

from scicheck.utils import check_type
from scicheck import _message
from scicheck.errors import (
    CannotConvertToPath,
    NotPathError,
    NotFileError,
    FileExistsError,
    FileNotFoundError,
    FolderExistsError,
    FolderNotFoundError,
    NotFolderError,
    FolderNotEmpty
)

if typing.TYPE_CHECKING:
    from typing import Any


def path(
    input: Any, 
    name: str = 'input', 
    *, 
    strict: bool = False, 
    resolve: bool = True
) -> Path:
    
    # Convert to path
    path = check_type(
        input, 
        Path, 
        name, 
        description = 'pathlib.Path object',
        strict=strict,
        NotTypeError = NotPathError,
        CannotConvertToType=CannotConvertToPath
    )

    # Optionally resolve
    if resolve:
        path = path.resolve()
    return path


#####
# File
#####


def _check_type(path: Path, type: str, name: str):
    
    # Get the validator and error associated with the type
    if type == 'file':
        valid = path.is_file()
        error = NotFileError
    elif type == 'folder':
        valid = path.is_dir()
        error = NotFolderError

    # Error if not valid
    if not valid:
        message = _message.wrong_path(name, path, type)
        raise error(message)


def _existing(input, type, name, strict, MissingError):
    input = path(input, name, strict=strict, resolve=True)
    if not input.exists():
        message = _message.missing(name, input)
        raise MissingError(message)
    _check_type(input, type, name)
    return input
 
    
def existing_file(input: Any, name: str = 'input', *, strict: bool = False):
    return _existing(input, 'file', name, strict, FileNotFoundError)

def existing_folder(input: Any, name: str = 'input', *, strict: bool = False):
    return _existing(input, 'folder', name, strict, FolderNotFoundError)

def _new(input, type, name, strict, exist_ok, ExistsError):

    input = path(input, name, strict=strict, resolve=True)
    if input.exists():
        if not exist_ok:
            message = _message.exists(name, path)
            raise ExistsError(message)
        _check_type(path, type, name)
    return input



def new_file(input: Any, name: str = 'input', *, strict: bool = False, exist_ok: bool = False):
    return _new(input, 'file', name, strict, exist_ok, FileExistsError)


def new_folder(
    input: Any, 
    name: str = 'input', 
    *, 
    strict: bool = False, 
    exist_ok: bool = False,
    require_empty: bool = True,
):
    
    folder = _new(input, 'folder', name, strict, exist_ok, FolderExistsError)
    if require_empty and any(folder.iterdir()):
        message = _message.not_empty(name, path)
        raise FolderNotEmpty(message)
    return folder


