# ununsed imports here, to bring them into scope for other files from sys import platform
from sys import platform
import sqlite3
import warnings

from pathlib import Path
from urllib.parse import unquote
from datetime import datetime, timezone
from typing import List, Iterator, Optional, NamedTuple
from dataclasses import dataclass

from ..log import logger
from ..model import Visit, Metadata
from ..common import PathIshOrConn, _func_if_some
from ..sqlite import _execute_query


@dataclass
class Schema:
    cols: List[str]
    where: str

    @property
    def query(self) -> str:
        return f"SELECT {', '.join(self.cols)} {self.where}"


@dataclass
class Browser:
    schema: Schema  # used to create the query to extract visit from database

    detector: str  # semi-unique name of table present on database to detect this type

    @classmethod
    def detect(cls, path: PathIshOrConn) -> bool:
        """
        Run the detector against the given path/connection to detect if the current Browser matches the schema
        """
        detector_query = f"SELECT * FROM {cls.detector}"
        logger.debug(f"{cls.__name__}: Running detector query '{detector_query}'")
        try:
            list(_execute_query(path, detector_query))
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
        """
        The local data directory for this browser
        """
        raise NotImplementedError

    @classmethod
    def locate_database(cls, profile: str) -> Path:
        """
        Locate this database on the users' computer so it can be backed up
        """
        raise NotImplementedError


def _from_datetime_microseconds(ts: int) -> datetime:
    return datetime.fromtimestamp(ts / 1_000_000, tz=timezone.utc)


errmsg = """Expected to match single database, got {}.
You can use the --profile argument to select one of the profiles/match a particular file"""


def _handle_glob(base: Path, stem: str, recursive: bool = False) -> Path:
    dbs: List[Path]
    if not recursive:
        # basic glob, in the same directory
        dbs = list(base.glob(stem))
    else:
        # recursively glob
        dbs = list(base.rglob(stem))
    recur_desc = "recursive" if recursive else "non recursive"
    logger.debug(f"Glob {base} with {stem} ({recur_desc}) matched {dbs}")
    if len(dbs) > 1:
        raise RuntimeError(errmsg.format(dbs))
    elif len(dbs) == 1:
        # found the match!
        return dbs[0]
    else:
        # if we werent trying to search recursively, try a recursive search as a fallback
        if not recursive:
            return _handle_glob(base, stem, recursive=True)
        else:
            raise RuntimeError(f"Could not find database, using '{base}' and '{stem}'")


def _warn_unknown(browser_name: str, default_behaviour: str = "linux") -> None:
    """
    Helper to warn unknown platform + browser combinations while I don't have all of them figured out
    """
    warnings.warn(
        f"""Not sure where {browser_name} history is installed on {platform}
Defaulting to {default_behaviour} behaviour...

If you're using a browser/platform this currently doesn't support, please make an issue
at https://github.com/seanbreckenridge/browserexport/issues/new with information.
In the meantime, you can point this directly at a history database using the --path flag"""
    )
