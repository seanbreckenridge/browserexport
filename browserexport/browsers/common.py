# ununsed imports here, to bring them into scope for other files
import sys
import sqlite3
import warnings

from itertools import chain
from pathlib import Path
from urllib.parse import unquote
from datetime import datetime, timezone
from typing import List, Iterator, Optional, NamedTuple, Dict, Union, Tuple, Sequence
from dataclasses import dataclass


from ..log import logger
from ..model import Visit, Metadata
from ..common import PathIsh, PathIshOrConn, func_if_some, expand_path
from ..sqlite import execute_query


@dataclass
class Schema:
    cols: List[str]
    where: str
    order_by: Optional[str] = None

    @property
    def query(self) -> str:
        qr = f"SELECT {', '.join(self.cols)} {self.where}"
        if self.order_by is not None:
            qr += f" ORDER BY {self.order_by}"
        return qr


Detector = str
Paths = Sequence[Path]


@dataclass
class Browser:
    schema: Schema  # used to create the query to extract visit from database
    detector: Detector  # semi-unique name of table, or a query to run on database to detect this type
    has_save: bool = True  # if this browser works with the save command
    has_form_history_save: bool = False  # if this can backup form history

    @classmethod
    def detect(cls, path: PathIshOrConn) -> bool:
        """
        Run the detector against the given path/connection to detect if the current Browser matches the schema
        """
        # if the user provided something that had spaces - is a query
        if " " in cls.detector.strip():
            detector_query = cls.detector
        else:
            detector_query = f"SELECT * FROM {cls.detector}"
        logger.debug(f"{cls.__name__}: Running detector query '{detector_query}'")
        try:
            list(execute_query(path, detector_query))
            return True
        except sqlite3.OperationalError as sql_err:
            logger.debug(str(sql_err))
            return False

    @classmethod
    def extract_visits(cls, path: PathIshOrConn) -> Iterator[Visit]:
        """
        Given a path or a sqlite3 connection, extract visits
        """
        raise NotImplementedError

    @classmethod
    def data_directory(cls) -> Path:
        warnings.warn("'data_directory' method is deprecated. Please switch to 'data_directories'")
        dirs = cls.data_directories()
        assert len(dirs) > 0
        if len(dirs) > 1:
            logger.warn('got multiple alternaitves for data directory, picking the first')
        return dirs[0]

    @classmethod
    def data_directories(cls) -> Paths:
        """
        The local data directories for this browser
        """
        raise NotImplementedError

    @classmethod
    def locate_database(cls, profile: str) -> Path:
        """
        Locate this database on the users' computer so it can be backed up
        """
        raise NotImplementedError

    @classmethod
    def locate_form_history(cls, profile: str) -> Path:
        """
        Locate the Form History (e.g. Usernames/Form fields) database so it can be backed up
        """
        raise NotImplementedError


def from_datetime_microseconds(ts: int) -> datetime:
    return datetime.fromtimestamp(ts / 1_000_000, tz=timezone.utc)


errmsg = """Expected to match single database, got {}.
You can use the --profile argument to select one of the profiles/match a particular file"""


def handle_glob(bases: Sequence[Path], stem: str, recursive: bool = False) -> Path:
    dbs: List[Path]
    method = Path.rglob if recursive else Path.glob
    dbs = list(chain(*[method(base, stem) for base in bases]))
    recur_desc = "recursive" if recursive else "non recursive"
    logger.debug(f"Glob {bases} with {stem} ({recur_desc}) matched {dbs}")
    if len(dbs) > 1:
        raise RuntimeError(errmsg.format(dbs))
    elif len(dbs) == 1:
        # found the match!
        return dbs[0]
    else:
        # if we werent trying to search recursively, try a recursive search as a fallback
        if not recursive:
            return handle_glob(bases, stem, recursive=True)
        else:
            raise RuntimeError(f"Could not find database, using '{bases}' and '{stem}'")


PathMapEntry = Union[PathIsh, Sequence[PathIsh]]


def handle_path(
    pathmap: Dict[str, PathMapEntry],
    browser_name: str,
    *,
    key: Optional[str] = None,
    default_behaviour: str = "linux",
) -> Paths:
    """
    Handles the repetitive task of having to resolve/expand a path
    which describes the location of the data directory on each
    opreating system
    """
    loc: Sequence[PathIsh]
    # if the user didn't provide a key, assume this is a 'sys.platform' map - using
    # darwin/linux to specify the location
    if key is None:
        key = sys.platform
    # use the key provided, or the first item (dicts after python3.7 are ordered)
    # in the pathmap if that doesnt exist
    maybeloc: Optional[PathMapEntry] = pathmap.get(key)
    if maybeloc is None:
        warnings.warn(
            f"""Not sure where {browser_name} history is installed on {sys.platform}
Defaulting to {default_behaviour} behaviour...

If you're using a browser/platform this currently doesn't support, please make an issue
at https://github.com/seanbreckenridge/browserexport/issues/new with information.
In the meantime, you can point this directly at a history database using the --path flag"""
        )
        maybeloc = pathmap[list(pathmap.keys())[0]]
    assert maybeloc is not None  # convince mypy
    if isinstance(maybeloc, (Path, str)):
        loc = [maybeloc]
    else:
        loc = maybeloc
    return tuple(expand_path(p) for p in loc)


def test_handle_path() -> None:

    import pytest
    import sys

    oldplatform = sys.platform

    sys.platform = "linux"

    from .firefox import Firefox

    expected_linux = (
        Path("~/.mozilla/firefox/").expanduser().absolute(),
        Path("~/snap/firefox/common/.mozilla/firefox/").expanduser().absolute(),
    )

    assert Firefox.data_directories() == expected_linux

    sys.platform = "darwin"
    assert Firefox.data_directories() == (
        Path("~/Library/Application Support/Firefox/Profiles/").expanduser().absolute(),
    )

    sys.platform = "something else"
    # should default to linux
    with pytest.warns(UserWarning, match=r"history is installed"):
        assert Firefox.data_directories() == expected_linux

    sys.platform = oldplatform
