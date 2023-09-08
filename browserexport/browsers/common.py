# ununsed imports here, to bring them into scope for other files
import os
import sys
import sqlite3

from itertools import chain
from pathlib import Path
from functools import lru_cache
from datetime import datetime, timezone
from typing import (
    List,
    Iterator,
    Optional,
    Dict,
    Union,
    Sequence,
)
from dataclasses import dataclass

import click

from ..log import logger
from ..model import Visit, Metadata
from ..common import PathIsh, PathIshOrConn, expand_path, BrowserexportError
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


def from_datetime_microseconds(ts: int) -> datetime:
    return datetime.fromtimestamp(ts / 1_000_000, tz=timezone.utc)


errmsg = """Expected to match a single database, but found:
{}

You can use the --profile argument to select one of the profiles/match a particular file"""


def handle_glob(bases: Sequence[Path], stem: str, recursive: bool = False) -> Path:
    dbs: List[Path]
    method = Path.rglob if recursive else Path.glob
    dbs = list(chain(*[method(base, stem) for base in bases]))
    recur_desc = "recursive" if recursive else "non recursive"
    logger.debug(f"Glob {bases} with {stem} ({recur_desc}) matched {dbs}")
    if len(dbs) > 1:
        human_readable_db_paths: str = "\n".join([str(db) for db in dbs])
        raise BrowserexportError(errmsg.format(human_readable_db_paths))
    elif len(dbs) == 1:
        # found the match!
        return dbs[0]
    else:
        # if we werent trying to search recursively, try a recursive search as a fallback
        if not recursive:
            return handle_glob(bases, stem, recursive=True)
        else:
            import shlex

            raise BrowserexportError(
                "Could not find database, using bases: '{bases}' and profile '{stem}'".format(
                    bases=", ".join(f'"{shlex.quote(str(base))}"' for base in bases),
                    stem=stem,
                )
            )


PROCFILE = Path("/proc/version")


@lru_cache(maxsize=1)
def determine_operating_system() -> str:
    # if this is being run from WSL, return win32
    # this should also detect cygwin as well
    if PROCFILE.exists():
        proc_version = PROCFILE.read_text()
        if "microsoft" in proc_version.lower():
            return "win32"
    return sys.platform


PathMapEntry = Union[PathIsh, Sequence[PathIsh]]


WINDOWS_BASE_ENVVARS = ("%LOCALAPPDATA%", "%APPDATA%")


# hmm, should this accept multiple paths?, callee could always
# just combine multiple calls to this function into one tuple
# and then pass that to handle_path
def windows_appdata_paths(path: str) -> Sequence[PathIsh]:
    """
    Given a path, return the path with the APPDATA/LOCALAPPDATA environment variables
    expanded.
    """
    # normpath converts the path to use the correct path separator for windows incase
    # the user provided a path with forward slashes
    return tuple(
        os.path.normpath(os.path.expandvars(os.path.join(envvar, path)))
        for envvar in WINDOWS_BASE_ENVVARS
    )


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
        key = determine_operating_system()
    # use the key provided, or the first item (dicts after python3.7 are ordered)
    # in the pathmap if that doesnt exist
    maybeloc: Optional[PathMapEntry] = pathmap.get(key)
    if maybeloc is None:
        click.echo(
            f"""Not sure where {browser_name} history is installed on {key}
Defaulting to {default_behaviour} behaviour...

If you're using a browser/platform this currently doesn't support, please make an issue
at https://github.com/seanbreckenridge/browserexport/issues/new with information.
In the meantime, you can point this directly at a history database using the --path flag""",
            err=True,
        )
        maybeloc = pathmap[list(pathmap.keys())[0]]
    assert maybeloc is not None  # convince mypy
    if isinstance(maybeloc, (Path, str)):
        loc = [maybeloc]
    else:
        loc = maybeloc
    return tuple(expand_path(p) for p in loc)
