import os
import glob
import tempfile
import json as jsn
from pathlib import Path
from typing import List

import click
import IPython  # type: ignore[import]

from .common import PathIsh
from .model import MozVisit, MozPlace, Visit
from .save_hist import backup_history
from .parse_db import single_db_visits, single_db_sitedata, single_db_merge
from .demo import demo_visit
from .merge_db import read_and_merge
from .serialize import serialize_visit, serialize_moz_place, serialize_moz_visit

# target for python3 -m ffexport and console_script using click
@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option(
    "--browser",
    type=click.Choice(["firefox", "chrome"], case_sensitive=False),
    default="firefox",
    help="Provide either 'firefox' or 'chrome' [defaults to firefox]",
)
@click.option(
    "--profile",
    type=str,
    default="*",
    help="Use to pick the correct profile to back up. If unspecified, will assume a single profile",
)
@click.option(
    "--to",
    type=click.Path(exists=True),
    required=True,
    help="Directory to store backup to",
)
def save(browser: str, profile: str, to: str) -> None:
    """
    Backs up the current firefox sqlite history file.
    """
    backup_history(browser=browser, profile=profile, to=to)


@cli.command()
@click.argument("SQLITE_DB", type=click.Path(exists=True), required=True)
@click.option(
    "--json",
    is_flag=True,
    default=False,
    required=False,
    help="Print result to STDOUT as JSON",
)
def inspect(sqlite_db: str, json: bool) -> None:
    """
    Extracts history/site metadata from one sqlite database.

    Provide a firefox history sqlite databases as the first argument.
    Drops you into a REPL to access the data.
    """
    mvis: List[MozVisit] = list(single_db_visits(sqlite_db))
    msite: List[MozPlace] = list(single_db_sitedata(sqlite_db))
    vis: List[Visit] = list(single_db_merge(mvis, msite))

    if json:
        print(
            jsn.dumps(
                {
                    "visits": list(map(serialize_moz_visit, mvis)),
                    "places": list(map(serialize_moz_place, msite)),
                }
            )
        )

    else:
        demo_visit(vis)
        IPython.embed(
            header="Use mvis or msite to access raw visits/site data, vis for the merged data"
        )


@cli.command()
@click.argument("SQLITE_DB", type=click.Path(exists=True), nargs=-1, required=True)
@click.option(
    "--include-live",
    is_flag=True,
    default=False,
    required=False,
    help="In addition to any provided databases, copy current (firefox) history to /tmp and merge it as well",
)
@click.option(
    "--browser",
    type=click.Choice(["firefox", "chrome"], case_sensitive=False),
    default="firefox",
    help="Provide either 'firefox' or 'chrome' [defaults to firefox]",
)
@click.option(
    "--profile",
    type=str,
    default="*",
    help="Use to pick the correct profile to back up. If unspecified, will assume a single profile",
)
@click.option(
    "--json",
    is_flag=True,
    default=False,
    required=False,
    help="Print result to STDOUT as JSON",
)
def merge(
    sqlite_db: List[str], include_live: bool, browser: str, profile: str, json: bool
) -> None:
    """
    Extracts history/site metadata from multiple sqlite databases.

    Provide multiple sqlite databases as positional arguments, e.g.:
    ffexport merge ~/data/firefox/dbs/*.sqlite

    Provides a similar interface to inspect;
    drops you into a REPL to access the data.
    """
    sqlite_dbs: List[PathIsh] = list(sqlite_db)
    # if we want to also include live history, include
    if include_live:
        # uhh may want to use mkdtemp here instead so that the tempdir isnt removed
        # *if* I wasn't consuming the generator immediately, the directory
        # might be deleted before read_and_merge is called for that iteration
        # https://docs.python.org/3/library/tempfile.html#tempfile.mkdtemp
        # however, since I am converting it to a list, should be fine in this case
        tmp_dir = tempfile.TemporaryDirectory()
        backup_history(browser=browser, profile=profile, to=Path(tmp_dir.name))
        live_copy: List[str] = glob.glob(os.path.join(tmp_dir.name, "*.sqlite"))
        assert (
            len(live_copy) == 1
        ), f"Couldn't find live history backup in {tmp_dir.name}"
        sqlite_dbs.append(live_copy[0])
    merged_vis: List[Visit] = list(read_and_merge(*sqlite_dbs))  # type: ignore[arg-type]
    if json:
        click.echo(jsn.dumps(list(map(serialize_visit, merged_vis))))
    else:
        IPython.embed(header="Use merged_vis to access merged data from all databases")
