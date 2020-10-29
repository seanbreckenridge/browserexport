"""
Merges multiple history sqlite databases into one
"""

import locale
import warnings
from datetime import datetime
from itertools import chain
from typing import Iterator, Sequence, Set, Tuple, List

from .log import logger
from .model import Visit
from .common import PathIsh, expand_paths
from .parse_db import read_visits

# https://stackoverflow.com/a/10742904/9348376
locale.setlocale(locale.LC_ALL, "")


def format_num(num: int) -> str:
    return f"{num:n}"


# not sure on the typing/Sequence's with splat here
# works fine though, each of these accept variadic arguments
# with either PathIsh-things or Iterator/List things w/ Visits


def read_and_merge(*input_databases: Sequence[PathIsh]) -> Iterator[Visit]:
    """
    Receives variable amount of PathIsh as input,
    reads Visits from each of those databases,
    and merges them together (removing duplicates)
    """
    database_histories: List[Iterator[Visit]] = list(
        map(read_visits, expand_paths(input_databases))  # type: ignore[arg-type]
    )
    yield from merge_visits(*database_histories)


def merge_visits(*sources: Iterator[Visit]) -> Iterator[Visit]:
    """
    Removes duplicate Visit items from multiple sources
    """
    if len(sources) == 0:
        warnings.warn("merge_visits received no sources!")
    else:
        logger.debug("merging information from {} databases...".format(len(sources)))
    # use combination of URL, visit date and visit type to uniquely identify visits
    emitted: Set[Tuple[str, datetime, int]] = set()
    duplicates = 0
    for vs in chain(*sources):
        key = (vs.url, vs.visit_date, vs.visit_type)
        if key in emitted:
            # logger.debug(f"skipping {key} => {vs}")
            duplicates += 1
            continue
        yield vs
        emitted.add(key)
    logger.debug("Summary: removed {} duplicates...".format(format_num(duplicates)))
    logger.debug(
        "Summary: returning {} visit entries...".format(format_num(len(emitted)))
    )
