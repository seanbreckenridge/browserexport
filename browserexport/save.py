from datetime import datetime
from pathlib import Path
from typing import Optional, Type, Union

from sqlite_backup import sqlite_backup

from .log import logger
from .common import PathIsh, expand_path
from .browsers.all import DEFAULT_BROWSERS
from .browsers.common import Browser


def _progress(status: str, remaining: int, total: int) -> None:
    logger.debug(f"Copied {total-remaining} of {total} database pages...")


def _sqlite_backup(src: PathIsh, dest: PathIsh) -> None:
    logger.info(f"backing up {src} to {dest}")
    sqlite_backup(
        src,
        dest,
        wal_checkpoint=True,
        copy_use_tempdir=True,
        sqlite_backup_kwargs={"progress": _progress},
    )


def _path_backup(src: PathIsh, dest: PathIsh) -> Path:
    """
    User specified the exact path to backup a database, back it up
    """
    srcp: Path = expand_path(src)
    destp: Path = _default_pattern(srcp, dest)
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
    save_type: Optional[str] = None,
) -> Path:
    """
    browser:
        typically the name of a browser the user provided from the CLI
        For library usage, user can pass a custom subclassed browser type which implements
            the required functions to locate the database
    to:
        path/string to backup database to
    profile:
        for browsers which have multiple profiles/users, this lets you specify
        a glob to select a particular profile
    pattern:
        pattern for the resulting timestamped filename, should include a format replacement field
    save_type:
        browser history, form history etc. If not supplied, assumes browser history
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
            raise RuntimeError(f"Unknown browser: {browser}")
    else:
        chosen = browser
        browser_name = chosen.__name__.lower()
    src: Path
    if save_type == "form_history":
        src = chosen.locate_form_history(profile)
    else:
        src = chosen.locate_database(profile)
    dest = _default_pattern(src, to, browser_name, pattern)
    _sqlite_backup(src, dest)
    return dest
