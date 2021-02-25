"""
Read/export visits and site data from firefox sqlite database exports
"""

# Could potentially pull in the other code for Chrome/Firefox-Mobile from
# https://github.com/karlicoss/promnesia/blob/master/src/promnesia/sources/browser.py
# but I don't expect Im switching to a chrome-based browser any time soon

import sqlite3

from urllib.parse import unquote
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import List, Iterator, Dict

from .log import logger
from .common import PathIsh, expand_path
from .model import MozVisit, MozPlace, Visit, StrMetadata


# individual visits to a website
VISIT_QUERY = """
SELECT P.url, P.id AS pid, V.id as vid,
V.visit_date, V.visit_type
FROM moz_historyvisits as V, moz_places as P
WHERE V.place_id = P.id
""".strip()

# get related title/description/preview image. This uses moz_places (which is a one-to-many relation with moz_historyvisits)
# see https://web.archive.org/web/20190730231715/https://www.forensicswiki.org/wiki/Mozilla_Firefox_3_History_File_Format#moz_historyvisits
SITEDATA_QUERY = """
SELECT P.id AS pid, P.title, P.description, P.preview_image_url FROM moz_places as P
WHERE P.title IS NOT NULL OR P.description IS NOT NULL OR P.preview_image_url IS NOT NULL
""".strip()

# combine the two queries above to extract all relevant info from a database
COMBINED_QUERY = """
SELECT P.url, V.visit_date, V.visit_type,
P.title, P.description, P.preview_image_url
FROM moz_historyvisits as V, moz_places as P
WHERE V.place_id = P.id
"""

# only need to do this once per sqlite path
@lru_cache(maxsize=None)
def sanity_check(sqlite_path: Path) -> None:
    with sqlite3.connect(f"file:{sqlite_path}?immutable=1", uri=True) as c:
        # sanity check to make sure the schema matches what we expect
        try:
            c.execute("SELECT * from moz_meta")
        except sqlite3.DatabaseError as sql_err:
            logger.error(
                "could not select from moz_meta; sqlite database not in the expected format"
            )
            logger.exception(sql_err)
            raise sql_err


# Referenced:
# https://github.com/karlicoss/promnesia/blob/8cb4af52df1e9307c7e2e3a35cc82e7a716cbe64/src/promnesia/sources/browser.py#L91
# https://github.com/karlicoss/promnesia/blob/8cb4af52df1e9307c7e2e3a35cc82e7a716cbe64/src/promnesia/sources/browser.py#L222


def execute_query(sqlite_path: Path, query: str) -> Iterator[sqlite3.Row]:
    sanity_check(sqlite_path)
    with sqlite3.connect(f"file:{sqlite_path}?immutable=1", uri=True) as c:
        c.row_factory = sqlite3.Row
        c.text_factory = lambda b: b.decode(errors="ignore")
        for row in c.execute(query):
            yield row


def single_db_visits(sqlite_path: PathIsh) -> Iterator[MozVisit]:
    """Connect to the sqlite database and extract visit information"""
    p = expand_path(sqlite_path)
    logger.debug(f"Reading individual visits from {p}...")
    for row in execute_query(p, VISIT_QUERY):
        # datetime looks like unix epoch
        # https://stackoverflow.com/a/19430099/706389
        yield MozVisit(
            # Replace %xx escapes (HTML chars) by their single-character equivalent
            url=unquote(row["url"]),
            place_id=row["pid"],
            visit_id=row["vid"],
            visit_date=datetime.fromtimestamp(
                row["visit_date"] / 1_000_000, timezone.utc
            ),
            visit_type=row["visit_type"],
        )


def single_db_sitedata(sqlite_path: PathIsh) -> Iterator[MozPlace]:
    """Connect to the sqlite database and extract site metadata (title/descriptions)"""
    p = expand_path(sqlite_path)
    logger.debug(f"Reading sitedata from {p}...")
    for row in execute_query(p, SITEDATA_QUERY):
        pimg: StrMetadata = row["preview_image_url"]
        yield MozPlace(
            place_id=row["pid"],
            title=row["title"],
            description=row["description"],
            preview_image=unquote(pimg) if pimg is not None else None,
        )


def single_db_merge(
    visit_list: List[MozVisit], site_list: List[MozPlace]
) -> Iterator[Visit]:
    """
    Combines the MozVisit and MozPlace entries from a single database into a 'Visit'
    """
    # create dict for places for fast access
    site_dict: Dict[int, MozPlace] = {}
    for s in site_list:
        site_dict[s.place_id] = s

    # convert MozVisit to Visits
    for v in visit_list:
        # title, description, preview image
        t = ds = pi = None
        if v.place_id in site_dict:
            s = site_dict[v.place_id]
            t = s.title
            ds = s.description
            pi = s.preview_image
        yield Visit(
            url=v.url,
            visit_date=v.visit_date,
            visit_type=v.visit_type,
            title=t,
            description=ds,
            preview_image=pi,
        )


def read_visits(sqlite_path: PathIsh) -> Iterator[Visit]:
    """
    Takes one sqlite database as input and returns 'Visit's
    """
    p = expand_path(sqlite_path)
    logger.debug(f"Reading visits from {p}...")
    for row in execute_query(p, COMBINED_QUERY):
        pimg: StrMetadata = row["preview_image_url"]
        yield Visit(
            url=unquote(row["url"]),
            visit_date=datetime.fromtimestamp(
                row["visit_date"] / 1_000_000, timezone.utc
            ),
            visit_type=row["visit_type"],
            title=row["title"],
            description=row["description"],
            preview_image=unquote(pimg) if pimg is not None else None,
        )
