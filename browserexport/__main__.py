import os
import glob
import tempfile
import json as jsn
from pathlib import Path
from typing import List, Optional, Sequence

import click
import IPython  # type: ignore[import]

from .common import PathIsh
from .model import Visit
from .save import backup_history
from .browsers.all import DEFAULT_BROWSERS
from .parse import read_visits
from .demo import demo_visit
from .merge import read_and_merge

# target for python3 -m browserexport and console_script using click
@click.group()
def cli() -> None:
    pass


browser_names = [b.__name__.lower() for b in DEFAULT_BROWSERS]


@cli.command()
@click.option(
    "-b",
    "--browser",
    type=click.Choice(browser_names, case_sensitive=False),
    required=True,
    help="Provide browser to backup, or specify directly with --path",
)
@click.option(
    "-p",
    "--profile",
    type=str,
    default="*",
    help="Use to pick the correct profile to back up. If unspecified, will assume a single profile",
)
@click.option(
    "--path",
    type=str,
    default=None,
    help="Specify a direct path to a firefox-like database to back up",
)
@click.option(
    "-t",
    "--to",
    type=click.Path(exists=True),
    default=".",
    help="Directory to store backup to",
)
def save(browser: str, profile: str, to: str, path: Optional[str]) -> None:
    """
    Backs up a current browser database file
    """
    # TODO: implement custom backup --path (basic glob)
    backup_history(browser, to, profile=profile)


def _handle_merge(dbs: List[str], json: bool) -> None:
    vis: List[Visit] = list(read_and_merge(dbs))
    if json:
        click.echo(jsn.dumps([v.serialize() for v in vis]))
    else:
        IPython.embed(header="Use vis to access visit data")


@cli.command()
@click.argument("SQLITE_DB", type=click.Path(exists=True), required=True)
@click.option(
    "-j",
    "--json",
    is_flag=True,
    default=False,
    required=False,
    help="Print result to STDOUT as JSON",
)
def inspect(sqlite_db: str, json: bool) -> None:
    """
    Extracts visits from a single sqlite database.

    Provide a history database as the first argument.
    Drops you into a REPL to access the data.
    """
    _handle_merge([sqlite_db], json)


@cli.command()
@click.argument("SQLITE_DB", type=click.Path(exists=True), nargs=-1, required=True)
@click.option(
    "-j",
    "--json",
    is_flag=True,
    default=False,
    required=False,
    help="Print result to STDOUT as JSON",
)
def merge(sqlite_db: Sequence[str], json: bool) -> None:
    """
    Extracts visits from multiple sqlite databases

    Provide multiple sqlite databases as positional arguments, e.g.:
    browserexport merge ~/data/firefox/*.sqlite

    Drops you into a REPL to access the data
    """
    _handle_merge(list(sqlite_db), json)


if __name__ == "__main__":
    cli(prog_name="browserexport")
