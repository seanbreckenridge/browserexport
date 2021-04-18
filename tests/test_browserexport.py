from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Sequence, List, cast
import sqlite3

import pytest

from browserexport.common import expand_path
from browserexport.model import Visit
from browserexport.parse import read_visits
from browserexport.merge import read_and_merge


def test_using_conn(firefox: Path) -> None:
    conn = sqlite3.connect(f"file:{str(expand_path(firefox))}?immutable=1", uri=True)
    try:
        visits = list(read_visits(conn))
    finally:
        conn.close()
    assert len(visits) == 4


def test_read_visits(firefox: Path) -> None:
    vs = list(read_visits(firefox))
    assert len(vs) == 4
    vs = list(read_visits(str(firefox)))  # can also accept strings
    assert len(vs) == 4


def test_serialize_visit(firefox: Path) -> None:
    v = next(read_visits(firefox))
    sr_v = v.serialize()
    assert isinstance(sr_v, dict)
    assert set(sr_v.keys()) == {
        "metadata",
        "url",
        "dt",
    }
    assert sr_v["dt"] == 1593250194.51375
    assert sr_v["metadata"] is None
    assert sr_v["url"] == "https://www.mozilla.org/privacy/firefox/"


def test_merge_db(firefox: Path) -> None:
    # two of the same, should remove duplicates
    # and be the same as read_visits
    dbs: Sequence[Path] = [firefox, firefox]
    unique_count = len(list(read_and_merge(dbs)))
    direct_read_count = len(list(read_visits(firefox)))
    assert unique_count == direct_read_count


def test_read_chrome(chrome: Path) -> None:
    vis = list(read_visits(chrome))
    assert len(vis) == 6
    assert vis[0].metadata is not None
    assert vis[0].metadata.title == "Development Server"
    expected = datetime(2021, 1, 17, 6, 16, 15, 902496, tzinfo=timezone.utc)
    assert vis[0].dt == expected
    has_dur = vis[-1]
    assert has_dur.metadata is not None
    assert has_dur.metadata.duration == 16


def test_read_waterfox(waterfox: Path) -> None:
    vis = list(read_visits(waterfox))
    assert len(vis) == 2
    assert vis[0].url == "http://youtube.com/"
    expected = datetime(2021, 4, 16, 18, 36, 45, 691215, tzinfo=timezone.utc)
    assert vis[0].dt == expected


def test_read_chomium(chromium: Path) -> None:
    vis = list(read_visits(chromium))
    assert len(vis) == 1
    assert vis[0].url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    expected = datetime(2021, 4, 17, 19, 22, 2, 251822, tzinfo=timezone.utc)
    assert vis[0].dt == expected


def test_read_brave(brave: Path) -> None:
    vis = list(read_visits(brave))
    assert len(vis) == 2
    assert vis[0].metadata is not None
    assert vis[0].metadata.title == "User Terms of Service | Basic Attention Token"
    expected = datetime(2021, 4, 17, 19, 30, 32, 885828, tzinfo=timezone.utc)
    assert vis[0].dt == expected


def test_read_palemoon(palemoon: Path) -> None:
    vis = list(read_visits(palemoon))
    assert len(vis) == 8
    assert vis[0].metadata is not None
    assert vis[0].metadata.title == "Pale Moon - Congratulations"
    expected = datetime(2021, 4, 16, 18, 23, 23, 264033, tzinfo=timezone.utc)
    assert vis[0].dt == expected


def test_read_safari(safari: Path) -> None:
    vis = list(read_visits(safari))
    assert len(vis) == 3
    v = vis[-1]
    assert v.metadata is not None
    assert (
        v.metadata.title
        == "album amalgam - https://github.com/seanbreckenridge/albums - Google Sheets"
    )
    expected = datetime(2021, 4, 18, 1, 3, 45, 293084, tzinfo=timezone.utc)
    assert v.dt == expected


def test_merge_different(chrome: Path, waterfox: Path) -> None:
    chrome_vis = list(read_visits(chrome))
    waterfox_vis = list(read_visits(waterfox))
    merged_vis = list(read_and_merge([chrome, waterfox]))
    assert chrome_vis + waterfox_vis == merged_vis


def _database(name: str) -> Path:
    p = Path(__file__).parent / "databases" / f"{name}.sqlite"
    assert p.exists()
    return p


# fixtures to make writing tests a bit easier
# though, maintaining them like this is quite annoying,
# maybe I could do some metaprogramming to define these
# functions....


@pytest.fixture()
def firefox() -> Iterator[Path]:
    yield _database("firefox")


@pytest.fixture()
def chromium() -> Iterator[Path]:
    yield _database("chromium")


@pytest.fixture()
def chrome() -> Iterator[Path]:
    yield _database("chrome")


@pytest.fixture()
def brave() -> Iterator[Path]:
    yield _database("brave")


@pytest.fixture()
def palemoon() -> Iterator[Path]:
    yield _database("palemoon")


@pytest.fixture()
def waterfox() -> Iterator[Path]:
    yield _database("waterfox")


@pytest.fixture()
def safari() -> Iterator[Path]:
    yield _database("safari")
