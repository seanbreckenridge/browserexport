from typing import Union, Sequence
from pathlib import Path

PathIsh = Union[str, Path]


def expand_path(path: PathIsh) -> Path:
    if isinstance(path, str):
        path = Path(path)
    return path.expanduser().absolute()


def expand_paths(paths: Sequence[PathIsh]) -> Sequence[Path]:
    return list(map(expand_path, paths))
