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
    differs = True
    while differs:
        res = shutil.copy(src, dest)
        differs = not filecmp.cmp(str(src), str(res))


def _handle_backup(src: Path, to: Path, *, pattern: Optional[str]) -> Path:
    """
    handle backing up the file w/ a timestamp, once its been located
    """
    # create pattern to timestamp backup filename
    now: str = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    pattern = src.stem + "-{}" + src.suffix if pattern is None else pattern
    res: Path = to / pattern.format(now)

    logger.debug("backing up %s to %s", src, res)
    atomic_copy(src, res)
    return res


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

    to_p: Path = expand_path(to)
    assert to_p.is_dir(), f"{to_p} is not a directory!"

    chosen: Type[Browser]
    if isinstance(browser, str):
        for extr in DEFAULT_BROWSERS:
            if browser.lower() == extr.__name__.lower():
                chosen = extr
                break
        else:
            raise RuntimeError(f"Unknown browser: {browser}")
    else:
        chosen = browser
    src: Path = chosen.locate_database(profile)
    return _handle_backup(src, to_p, pattern=browser.lower() + "-{}")
