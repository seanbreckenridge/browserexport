from datetime import datetime
from pathlib import Path
from typing import Iterator, Sequence, List

import pytest

from ffexport.common import expand_path
from ffexport.model import MozPlace, MozVisit, Visit
from ffexport.parse_db import (
    sanity_check,
    single_db_visits,
    single_db_sitedata,
    single_db_merge,
    read_visits,
)
from ffexport.serialize import serialize_visit
from ffexport.merge_db import read_and_merge


def test_sanity_check(database: Path) -> None:
    assert database.exists()
    sanity_check(database)


def test_single_db_visits(database: Path) -> None:
    mv = list(single_db_visits(database))
    assert len(mv) == 5
    assert all([type(m) == MozVisit for m in mv])
    fv = mv[0]
    assert fv.url == "https://www.mozilla.org/privacy/firefox/"
    assert fv.place_id == 1
    assert fv.visit_id == 1
    assert fv.visit_type == 1
    assert isinstance(fv.visit_date, datetime)


def test_single_db_sitedata(database: Path) -> None:
    sd = list(single_db_sitedata(database))
    assert len(sd) == 2
    assert all([type(s) == MozPlace for s in sd])
    fs = sd[0]
    assert fs.place_id == 2
    assert fs.title is not None
    assert fs.title == "Firefox Developer Edition"
    assert fs.description is not None
    assert fs.description.startswith(
        "Firefox Developer Edition is the blazing fast browser"
    )


def test_single_db_merge(database: Path) -> None:
    vs = list(
        single_db_merge(
            list(single_db_visits(database)), list(single_db_sitedata(database))
        )
    )
    assert len(vs) == 5
    assert all([type(v) == Visit for v in vs])
    fv = vs[1]  # first has no title, use second
    assert vs[0].description is None
    assert fv.url == "https://www.mozilla.org/en-US/firefox/78.0a2/firstrun/"
    assert fv.visit_date.year == 2020
    assert fv.description is not None
    assert fv.description.startswith(
        "Firefox Developer Edition is the blazing fast browser that offers cutting edge developer"
    )
    assert fv.preview_image is not None
    assert (
        fv.preview_image
        == "https://www.mozilla.org/media/protocol/img/logos/firefox/browser/developer/og.0e5d59686805.png"
    )


def test_read_visits(database: Path) -> None:
    vs = list(read_visits(database))
    assert len(vs) == 5
    vs = list(read_visits(str(database)))  # can also accept strings
    assert len(vs) == 5


def test_serialize_visit(database: Path) -> None:
    v = next(read_visits(database))
    assert isinstance(v, Visit)
    sr_v = serialize_visit(v)
    assert isinstance(sr_v, dict)
    assert set(sr_v.keys()) == {
        "description",
        "preview_image",
        "title",
        "url",
        "visit_date",
        "visit_type",
    }
    assert sr_v["visit_date"] == 1593250194
    assert sr_v["description"] == None
    assert sr_v["url"] == "https://www.mozilla.org/privacy/firefox/"


def test_merge_db(database: Path) -> None:
    # two of the same, should remove duplicates
    # and be the same as read_visits
    dbs: Sequence[Path] = [database, database]
    # read and merge uses read_visits, which removes duplicate visits
    assert len(list(read_and_merge(*dbs))) + 1 == len(list(read_visits(database)))  # type: ignore


def test_manual_merge_db(database: Path) -> None:
    # manual sitedata + visit query merging should be the same as read_visits
    p = expand_path(database)
    # use a dict/lookup to merge lists of mvis and msite using the common ids
    mvis: List[MozVisit] = list(single_db_visits(p))
    msite: List[MozPlace] = list(single_db_sitedata(p))
    manual_merged: List[Visit] = list(single_db_merge(mvis, msite))
    # read already merged from db
    sql_merged: List[Visit] = list(read_visits(database))
    assert len(sql_merged) == len(manual_merged)
    assert set(sql_merged) == set(manual_merged)


@pytest.fixture()
def database() -> Iterator[Path]:
    db_path: Path = Path(__file__).parent / "db.sqlite"
    yield db_path
