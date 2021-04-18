import logging
import json as jsn
from typing import List, Optional, Sequence, Callable

import click
import IPython  # type: ignore[import]

from .model import Visit
from .save import backup_history, _path_backup
from .browsers.all import DEFAULT_BROWSERS
from .merge import read_and_merge
from .demo import demo_visit
from .log import setup

# target for python3 -m browserexport and console_script using click
@click.group()
@click.option("--debug", is_flag=True, default=False, help="Increase log verbosity")
def cli(debug: bool) -> None:
    """
    Backup and merge your browser history!
    """
    if debug:
        setup(logging.DEBUG)


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
    type=click.Path(exists=True),
    default=None,
    help="Specify a direct path to a database to back up",
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
    if path is not None:
        # TODO: add profile to do a basic glob/make --path easier to use?
        # could be confusing. for now, forcing the user to specify full path
        # hopefully this isn't needed a lot/can be replaced by
        # additional Browser+platform specific default paths
        _path_backup(path, to)
        return
    backup_history(browser, to, profile=profile)


def _handle_merge(dbs: List[str], json: bool) -> None:
    vis: List[Visit] = list(read_and_merge(dbs))
    if json:
        click.echo(jsn.dumps([v.serialize() for v in vis]))
    else:
        demo_visit(vis)
        header = f"Use {click.style('vis', fg='green')} to access visit data"
        IPython.embed(header=header)


SHARED = [
    click.option(
        "-j",
        "--json",
        is_flag=True,
        default=False,
        required=False,
        help="Print result to STDOUT as JSON",
    )
]


# decorator to apply shared arguments to inpsect/merge
def shared_options(func: Callable[..., None]) -> Callable[..., None]:
    for decorator in SHARED:
        func = decorator(func)
    return func


@cli.command()
@click.argument("SQLITE_DB", type=click.Path(exists=True), required=True)
@shared_options
def inspect(sqlite_db: str, json: bool) -> None:
    """
    Extracts visits from a single sqlite database

    \b
    Provide a history database as the first argument
    Drops you into a REPL to access the data
    """
    _handle_merge([sqlite_db], json)


@cli.command()
@click.argument("SQLITE_DB", type=click.Path(exists=True), nargs=-1, required=True)
@shared_options
def merge(sqlite_db: Sequence[str], json: bool) -> None:
    """
    Extracts visits from multiple sqlite databases

    \b
    Provide multiple sqlite databases as positional arguments, e.g.:
    browserexport merge ~/data/firefox/*.sqlite

    Drops you into a REPL to access the data
    """
    _handle_merge(list(sqlite_db), json)


if __name__ == "__main__":
    cli(prog_name="browserexport")
