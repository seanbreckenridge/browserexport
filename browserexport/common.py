from typing import Union, TypeVar, Callable, Optional
from pathlib import Path
from sqlite3 import Connection

PathIsh = Union[str, Path]
# a path or a connection to a database
PathIshOrConn = Union[PathIsh, Connection]


def expand_path(path: PathIsh) -> Path:
    if isinstance(path, str):
        path = Path(path)
    return path.expanduser().absolute()


T = TypeVar("T")

# if 'maybe' is not None, run the specified function
def _func_if_some(maybe: Optional[T], func: Callable[[T], T]) -> Optional[T]:
    if maybe is not None:
        return func(maybe)
    return maybe
