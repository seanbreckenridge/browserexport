#!/usr/bin/env python3

# modified from https://github.com/karlicoss/promnesia/blob/master/scripts/browser_history.py

import filecmp
from datetime import datetime
from pathlib import Path
from subprocess import check_output
from typing import Optional

from .log import logger
from .common import PathIsh, expand_path

Browser = str

CHROME = "chrome"
FIREFOX = "firefox"


def get_path(browser: Browser, profile: str = "*") -> Path:
    if browser == "chrome":
        bpath = Path("~/.config/google-chrome").expanduser()
        dbs = bpath.glob(profile + "/History")
    elif browser == "firefox":
        bpath = Path("~/.mozilla/firefox/").expanduser()
        dbs = bpath.glob(profile + "/places.sqlite")
    else:
        raise RuntimeError(f"Unexpected browser {browser}")
    ldbs = list(dbs)
    if len(ldbs) == 1:
        return ldbs[0]
    raise RuntimeError(
        f"Expected single database, got {ldbs}. Perhaps you want to use --profile argument?"
    )


def atomic_copy(src: Path, dest: Path) -> None:
    """
    Supposed to handle cases where the file is changed while we were copying it.
    """
    import shutil

    differs = True
    while differs:
        res = shutil.copy(src, dest)
        differs = not filecmp.cmp(str(src), str(res))


def format_dt(dt: datetime) -> str:
    return dt.strftime("%Y%m%d%H%M%S")


def backup_history(
    browser: Browser, to: PathIsh, profile: str = "*", pattern: Optional[str] = None
) -> Path:
    to_p: Path = expand_path(to)
    assert to_p.is_dir()

    now = format_dt(datetime.utcnow())

    path = get_path(browser, profile=profile)

    pattern = path.stem + "-{}" + path.suffix if pattern is None else pattern
    fname = pattern.format(now)

    res: Path = to_p / fname
    logger.debug("backing up %s to %s", path, res)
    # if your chrome is open, database would normally be locked, so you can't just make a snapshot
    # so we'll just copy it till it converge. bit paranoid, but should work
    atomic_copy(path, res)
    logger.debug("done!")
    return res


def guess_db_date(db: Path) -> str:
    maxvisit = (
        check_output(
            [
                "sqlite3",
                "-csv",
                db,
                'SELECT max(datetime(((visits.visit_time/1000000)-11644473600), "unixepoch")) FROM visits;',
            ]
        )
        .decode("utf8")
        .strip()
        .strip('"')
    )
    return format_dt(datetime.strptime(maxvisit, "%Y-%m-%d %H:%M:%S"))


def test_guess(tmp_path: str) -> None:
    tdir = Path(tmp_path)
    db = backup_history(CHROME, tdir)
    guess_db_date(db)


def test_get_path() -> None:
    get_path("chrome")
    get_path("firefox", profile="*-release")


def test_backup_history(tmp_path: str) -> None:
    tdir = Path(tmp_path)
    backup_history(CHROME, tdir)
    backup_history(FIREFOX, tdir, profile="*-release")
