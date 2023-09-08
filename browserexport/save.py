import os
import sys
import sqlite3
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Type, Union

import click
from sqlite_backup import sqlite_backup

from .log import logger
from .common import PathIsh, expand_path, BrowserexportError
from .browsers.all import DEFAULT_BROWSERS
from .browsers.common import Browser


def _progress(status: str, remaining: int, total: int) -> None:
    logger.debug(f"Copied {total-remaining} of {total} database pages...")


def _sqlite_backup(src: PathIsh, dest: Optional[Path]) -> Optional[sqlite3.Connection]:
    logger.info(f"backing up {src} to {dest}")
    return sqlite_backup(
        src,
        dest,
        wal_checkpoint=True,
        copy_use_tempdir=True,
        sqlite_backup_kwargs={"progress": _progress},
    )


def _print_sqlite_db_to_stdout(pth: Path) -> None:
    force = "BROWEREXPORT_FORCE" in os.environ
    # make sure the user is piping this to something else, otherwise dont print
    if click.get_text_stream("stdout").isatty() and not force:
        logger.error(
            "stdout is a TTY, not printing database to stdout. Pipe to something else (e.g. browserexport save ... > db.sqlite, browserexport save ... | gzip --best > db.sqlite.gz) or set BROWEREXPORT_FORCE=1 to print to stdout"
        )
        return

    logger.debug("writing bytes to stdout...")
    with open(pth, "rb") as f:
        shutil.copyfileobj(f, sys.stdout.buffer)  # type: ignore[misc]
        sys.stdout.buffer.flush()


def _path_backup(
    src: PathIsh,
    dest: PathIsh,
    browser_name: Optional[str] = None,
    pattern: Optional[str] = None,
) -> Optional[Path]:
    """
    Backup from src to dest. If dest is '-', print to stdout

    Otherwise, return the path to the backup
    """
    srcp: Path = expand_path(src)
    if str(dest) == "-":
        # use temporary directory as its more windows-friendly
        with tempfile.TemporaryDirectory() as td:
            tfp = Path(tempfile.mktemp(suffix="-browser-stdin.sqlite", dir=td))
            _sqlite_backup(srcp, tfp)
            _print_sqlite_db_to_stdout(tfp)

        assert not tfp.exists(), f"expected {tfp} to be deleted, but it still exists!"
        return None
    else:
        destp: Path = _default_pattern(
            srcp, dest, browser_name=browser_name, pattern=pattern
        )
        _sqlite_backup(srcp, destp)
        return destp


def _default_pattern(
    src: Path,
    to: PathIsh,
    browser_name: Optional[str] = None,
    pattern: Optional[str] = None,
) -> Path:
    """
    can pass a pattern with a format replacement field (for the timestamp)
    if you'd rather use a different format

    by default, this appends sqlite if thats not already the suffix,
    adds the name of the browser and a timestamp
    """
    to_p: Path = expand_path(to)
    assert to_p.is_dir(), f"{to_p} is not a directory!"
    suffix = src.suffix or ".sqlite"
    if pattern is None:
        pattern = (browser_name or "browser") + "-{}" + suffix
    # create pattern to timestamp backup filename
    now: str = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return to_p / pattern.format(now)


def backup_history(
    browser: Union[str, Type[Browser]],
    to: PathIsh,
    *,
    profile: str = "*",
    pattern: Optional[str] = None,
) -> Optional[Path]:
    """
    browser:
        typically the name of a browser the user provided from the CLI
        For library usage, user can pass a custom subclassed browser type which implements
            the required functions to locate the database
    to:
        path/string to backup database to. If '-', print to stdout
    profile:
        for browsers which have multiple profiles/users, this lets you specify
        a glob to select a particular profile
    pattern:
        pattern for the resulting timestamped filename, should include an str.format replacement placeholder

    returns:
        path to the backup, or None if printing to stdout
    """

    chosen: Type[Browser]
    browser_name: str
    if isinstance(browser, str):
        for extr in DEFAULT_BROWSERS:
            if browser.lower() == extr.__name__.lower():
                chosen = extr
                browser_name = browser.lower()
                break
        else:
            raise BrowserexportError(f"Unknown browser: {browser}")
    else:
        chosen = browser
        browser_name = chosen.__name__.lower()
    src: Path = chosen.locate_database(profile)
    dest: Optional[Path] = _path_backup(
        src, to, browser_name=browser_name, pattern=pattern
    )
    if str(to) == "-":
        assert (
            dest is None
        ), f"expected dest to be None since we printed to stdout, got {dest}"
    return dest
