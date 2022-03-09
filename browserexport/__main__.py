import sys
import logging
import json as jsn
from typing import List, Optional, Sequence, Iterator

import click

from .browsers.all import DEFAULT_BROWSERS

CONTEXT_SETTINGS = {
    "max_content_width": 110,
    "show_default": True,
}


# target for python3 -m browserexport and console_script using click
@click.group(context_settings=CONTEXT_SETTINGS)
@click.option("--debug", is_flag=True, default=False, help="Increase log verbosity")
def cli(debug: bool) -> None:
    """
    Backup and merge your browser history!
    """
    from .log import setup

    if debug:
        setup(logging.DEBUG)


browsers_have_save = [b.__name__.lower() for b in DEFAULT_BROWSERS if b.has_save]

browsers_have_form_save = [
    b.__name__.lower() for b in DEFAULT_BROWSERS if b.has_form_history_save
]

# define click options
profile = click.option(
    "-p",
    "--profile",
    type=str,
    default="*",
    help="Use to pick the correct profile to back up. If unspecified, will assume a single profile",
)

path = click.option(
    "--path",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Specify a direct path to a database to back up",
)

store_to = click.option(
    "-t",
    "--to",
    type=click.Path(exists=True, file_okay=False),
    required=True,
    help="Directory to store backup to",
)

print_json = click.option(
    "-j",
    "--json",
    is_flag=True,
    default=False,
    required=False,
    help="Print result to STDOUT as JSON",
)

stream_json = click.option(
    "-s",
    "--stream",
    is_flag=True,
    default=False,
    required=False,
    help="Stream JSON objects instead of printing a JSON list",
)


@cli.command()
@click.option(
    "-b",
    "--browser",
    type=click.Choice(browsers_have_save, case_sensitive=False),
    required=False,
    help="Browser name to backup history for",
)
@click.option(
    "--form-history",
    type=click.Choice(browsers_have_form_save, case_sensitive=False),
    required=False,
    help="Browser name to backup form (input field) history for",
)
@profile
@path
@store_to
@click.pass_context
def save(
    ctx: click.Context,
    browser: Optional[str],
    form_history: Optional[str],
    profile: str,
    to: str,
    path: Optional[str],
) -> None:
    """
    Backs up a current browser database file
    """
    from .save import backup_history, _path_backup

    if path is not None:
        _path_backup(path, to)
    elif form_history is not None:
        backup_history(form_history, to, profile=profile, save_type="form_history")
    elif browser is not None:
        backup_history(browser, to, profile=profile)
    else:
        click.secho(
            "Error: must provide one of '--browser', '--form-history', or '--path'",
            err=True,
            fg="red",
        )
        click.echo(ctx.get_help())


def _handle_merge(dbs: List[str], *, json: bool, stream: bool) -> None:
    from .model import Visit
    from .merge import read_and_merge

    ivis: Iterator[Visit] = read_and_merge(dbs)
    if json or stream:
        if stream:
            for v in ivis:
                sys.stdout.write(jsn.dumps(v.serialize()))
            sys.stdout.flush()
        else:
            click.echo(jsn.dumps([v.serialize() for v in ivis]))
    else:
        import IPython  # type: ignore[import]

        from .demo import demo_visit

        vis: List[Visit] = list(ivis)
        demo_visit(vis)
        header = f"Use {click.style('vis', fg='green')} to access visit data"

        IPython.embed(header=header)


@cli.command()
@click.argument(
    "SQLITE_DB", type=click.Path(exists=True, dir_okay=False), required=True
)
@stream_json
@print_json
def inspect(sqlite_db: str, json: bool, stream: bool) -> None:
    """
    Extracts visits from a single sqlite database

    \b
    Provide a history database as the first argument
    Drops you into a REPL to access the data
    """
    _handle_merge([sqlite_db], json=json, stream=stream)


@cli.command()
@click.argument(
    "SQLITE_DB", type=click.Path(exists=True, dir_okay=False), nargs=-1, required=True
)
@stream_json
@print_json
def merge(sqlite_db: Sequence[str], json: bool, stream: bool) -> None:
    """
    Extracts visits from multiple sqlite databases

    \b
    Provide multiple sqlite databases as positional arguments, e.g.:
    browserexport merge ~/data/firefox/*.sqlite

    Drops you into a REPL to access the data
    """
    _handle_merge(list(sqlite_db), json=json, stream=stream)


if __name__ == "__main__":
    cli(prog_name="browserexport")
