from typing import Union, Sequence
from pathlib import Path
from sqlite3 import Connection

PathIsh = Union[str, Path]
# a path or a connection to a database
PathIshOrConn = Union[PathIsh, Connection]


def expand_path(path: PathIsh) -> Path:
    if isinstance(path, str):
        path = Path(path)
    return path.expanduser().absolute()


def expand_paths(paths: Sequence[PathIsh]) -> Sequence[Path]:
    return list(map(expand_path, paths))
