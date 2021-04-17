from datetime import datetime
from pathlib import Path
from typing import Iterator, Sequence, List
import sqlite3

import pytest

from browserexport.common import expand_path
from browserexport.model import Visit
from browserexport.parse import read_visits
from browserexport.merge import read_and_merge


def test_using_conn(database: Path) -> None:
    conn = sqlite3.connect(f"file:{str(expand_path(database))}?immutable=1", uri=True)
    try:
        visits = list(read_visits(conn))
    finally:
        conn.close()
    assert len(visits) == 5


def test_read_visits(database: Path) -> None:
    vs = list(read_visits(database))
    assert len(vs) == 5
    vs = list(read_visits(str(database)))  # can also accept strings
    assert len(vs) == 5


def test_serialize_visit(database: Path) -> None:
    v = next(read_visits(database))
    assert isinstance(v, Visit)
    sr_v = v.serialize()
    assert isinstance(sr_v, dict)
    assert set(sr_v.keys()) == {
        "description",
        "preview_image",
        "title",
        "url",
        "visit_date",
    }
    assert sr_v["visit_date"] == 1593250194.51375
    assert sr_v["description"] == None
    assert sr_v["url"] == "https://www.mozilla.org/privacy/firefox/"


def test_merge_db(database: Path) -> None:
    # two of the same, should remove duplicates
    # and be the same as read_visits
    dbs: Sequence[Path] = [database, database]
    # read and merge uses read_visits, which removes duplicate visits
    assert len(list(read_and_merge(dbs))) + 1 == len(list(read_visits(database)))  # type: ignore


@pytest.fixture()
def database() -> Iterator[Path]:
    db_path: Path = Path(__file__).parent / "firefox.sqlite"
    yield db_path
