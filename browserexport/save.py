import shutil
import filecmp
from datetime import datetime
from pathlib import Path
from typing import Optional, Type, Union

from .log import logger
from .common import PathIsh, expand_path

from .browsers.all import DEFAULT_BROWSERS
from .browsers.common import Browser


def atomic_copy(src: Path, dest: Path) -> None:
    """
    Supposed to handle cases where the file is changed while we were copying it.
    """
    # if your chrome is open, database would normally be locked, so you can't just make a snapshot
    # so we'll just copy it till it converge. bit paranoid, but should work
    logger.info("backing up %s to %s", src, dest)
    differs = True
    while differs:
        res = shutil.copy(src, dest)
        differs = not filecmp.cmp(str(src), str(res))


def _path_backup(src: PathIsh, dest: PathIsh) -> Path:
    """
    User specified the exact path to backup a database, atomically copy it
    """
    srcp: Path = expand_path(src)
    destp: Path = _default_pattern(srcp, dest)
    atomic_copy(srcp, destp)
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
    src: Path = chosen.locate_database(profile)
    res = _default_pattern(src, to, browser_name, pattern)
    atomic_copy(src, res)
    return res
