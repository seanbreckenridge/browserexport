from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Sequence
import sqlite3

import pytest

from browserexport.common import expand_path
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
    vis = list(read_visits(firefox))
    assert len(vis) == 4
    vis = list(read_visits(str(firefox)))  # can also accept strings
    assert len(vis) == 4


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


def test_read_vivaldi(vivaldi: Path) -> None:
    vis = list(read_visits(vivaldi))
    assert len(vis) == 3
    v = vis[-1]
    assert v.metadata is not None
    assert (
        v.metadata.title
        == "GitHub - seanbreckenridge/browserexport: backup and parse browser history databases"
    )
    expected = datetime(2021, 4, 19, 2, 26, 8, 29825, tzinfo=timezone.utc)
    assert v.dt == expected


def test_read_firefox_mobile_current(firefox_mobile: Path) -> None:
    vis = list(read_visits(firefox_mobile))
    assert len(vis) == 5
    v = vis[-1]
    assert v.url == "https://en.m.wikipedia.org/wiki/Vannevar_Bush"
    assert v.dt == datetime(2022, 2, 12, 8, 57, 19, 398000, tzinfo=timezone.utc)
    meta = v.metadata
    assert meta is not None
    assert meta.title == "Vannevar Bush - Wikipedia"
    assert meta.preview_image is not None


def test_read_firefox_mobile_legacy(firefox_mobile_legacy: Path) -> None:
    vis = list(read_visits(firefox_mobile_legacy))
    assert len(vis) == 3
    [v0, v1, v2] = vis
    assert v0.url == "https://github.com/"
    assert v0.dt == datetime(2020, 4, 11, 0, 54, 49, 44814, tzinfo=timezone.utc)
    assert v1.url == "https://xi.zulipchat.com/#"
    assert v1.dt == datetime(2020, 5, 28, 16, 18, 37, 6035, tzinfo=timezone.utc)
    v1meta = v1.metadata
    assert v1meta is not None, v1
    assert v1meta.title == "home - xi-editor and related projects - Zulip"
    assert v2.url == "https://github.com/"
    assert v2.dt == datetime(2020, 6, 27, 17, 34, 1, 963730, tzinfo=timezone.utc)


def test_merge_different(chrome: Path, waterfox: Path) -> None:
    chrome_vis = list(read_visits(chrome))
    waterfox_vis = list(read_visits(waterfox))
    merged_vis = list(read_and_merge([chrome, waterfox]))
    assert chrome_vis + waterfox_vis == merged_vis


def is_gz_file(filepath: Path) -> bool:
    with open(filepath, "rb") as test_f:
        # magic number for gzip files
        return test_f.read(2) == b"\x1f\x8b"


def test_read_json_dump(json_dump: Path) -> None:
    json_vis = list(read_visits(json_dump))
    assert not is_gz_file(json_dump)
    assert len(json_vis) == 1
    v = json_vis[0]
    assert v.url == "https://github.com/junegunn/fzf"
    assert v.dt == datetime(2020, 9, 15, 1, 29, 23, 720000, tzinfo=timezone.utc)
    assert v.metadata is not None
    assert v.metadata.preview_image == "https://github.com/favicon.ico"


def test_read_jsonl(jsonl_dump: Path) -> None:
    assert jsonl_dump.name.endswith(".jsonl")
    assert not is_gz_file(jsonl_dump)
    json_vis = list(read_visits(jsonl_dump))
    assert len(json_vis) == 3
    assert json_vis[0].url == "https://github.com/junegunn/fzf"
    assert json_vis[0].dt == datetime(
        2020, 9, 15, 1, 29, 23, 720000, tzinfo=timezone.utc
    )
    assert json_vis[1].url == "https://github.com/junegunn/fzf#installation"

    assert json_vis[1].metadata is not None
    assert json_vis[2].metadata is None


def test_read_json_gz(json_gz_dump: Path) -> None:
    assert json_gz_dump.name.endswith(".json.gz")
    assert is_gz_file(json_gz_dump)
    json_vis = list(read_visits(json_gz_dump))
    assert len(json_vis) == 1
    assert json_vis[0].url == "https://github.com/junegunn/fzf"


def test_read_jsonl_gz(jsonl_gz_dump: Path) -> None:
    assert jsonl_gz_dump.name.endswith(".jsonl.gz")
    assert is_gz_file(jsonl_gz_dump)
    json_vis = list(read_visits(jsonl_gz_dump))
    assert len(json_vis) == 2
    assert json_vis[0].url == "https://github.com/junegunn/fzf"
    assert json_vis[1].url == "https://github.com/junegunn/fzf#installation"


def test_mixed_read(json_dump: Path, firefox: Path) -> None:
    jvis = list(read_visits(json_dump))
    fvisits = list(read_visits(firefox))
    assert len(jvis + fvisits) == 5
    assert len(list(read_and_merge([json_dump, firefox]))) == 5


databases_dir: Path = Path(__file__).parent / "databases"


def _database(name: str) -> Path:
    p = databases_dir / f"{name}.sqlite"
    assert p.exists()
    return p


# fixtures to make writing tests a bit easier
# though, maintaining them like this is quite annoying...


@pytest.fixture()
def json_dump() -> Iterator[Path]:
    p = databases_dir / "merged_dump.json"
    assert p.exists()
    yield p


@pytest.fixture()
def jsonl_dump() -> Iterator[Path]:
    p = databases_dir / "merged_dump.jsonl"
    assert p.exists()
    yield p


@pytest.fixture()
def json_gz_dump() -> Iterator[Path]:
    p = databases_dir / "merged_dump.json.gz"
    assert p.exists()
    yield p


@pytest.fixture()
def jsonl_gz_dump() -> Iterator[Path]:
    p = databases_dir / "merged_dump.jsonl.gz"
    assert p.exists()
    yield p


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


@pytest.fixture()
def vivaldi() -> Iterator[Path]:
    yield _database("vivaldi")


@pytest.fixture()
def firefox_mobile() -> Iterator[Path]:
    yield _database("firefox_mobile")


@pytest.fixture()
def firefox_mobile_legacy() -> Iterator[Path]:
    yield _database("firefox_mobile_legacy")
