import sys
import os
import logging
import json as jsn
from contextlib import contextmanager
from typing import List, Optional, Sequence, Iterator

import click

from .browsers.all import DEFAULT_BROWSERS
from .common import BrowserexportError
from .log import logger

CONTEXT_SETTINGS = {
    "max_content_width": 110,
    "show_default": True,
    "help_option_names": ["-h", "--help"],
}


# target for python3 -m browserexport and console_script using click
@click.group(
    context_settings=CONTEXT_SETTINGS,
    epilog="For more info, see https://github.com/seanbreckenridge/browserexport",
)
@click.option("--debug", is_flag=True, default=False, help="Increase log verbosity")
def cli(debug: bool) -> None:
    """
    Backup and merge your browser history!
    """
    from .log import setup

    if debug:
        setup(logging.DEBUG)


browsers_have_save: List[str] = [
    b.__name__.lower() for b in DEFAULT_BROWSERS if b.has_save
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


@contextmanager
def _wrap_browserexport_cli_errors() -> Iterator[None]:
    try:
        yield
    except BrowserexportError as e:
        logger.debug(e, exc_info=True)
        click.echo(
            f"{click.style('Error:', 'red')} {e}, run as 'browserexport --debug' for more info"
        )
        exit(1)


def _wrapped_browser_list() -> str:
    import textwrap

    # split into groups of 6
    lines: List[List[str]] = []
    for i, b in enumerate(browsers_have_save):
        if i % 6 == 0:
            lines.append([])
        lines[-1].append(b)

    lines_fmted = [" | ".join(br) for br in lines]

    lines_fmted[0] = "<" + lines_fmted[0]
    lines_fmted[-1] = lines_fmted[-1] + ">"

    for i in range(0, len(lines_fmted) - 1):
        lines_fmted[i] = lines_fmted[i] + " |"

    return textwrap.indent("\n" + "\n".join(lines_fmted), " " * 6)


@cli.command(
    epilog="For a list of all browsers, run 'LIST_BROWSERS=1 browserexport save --help'"
)
@click.option(
    "-b",
    "--browser",
    type=click.Choice(browsers_have_save, case_sensitive=False),
    metavar="BROWSER" if "LIST_BROWSERS" not in os.environ else _wrapped_browser_list(),
    required=False,
    help="Browser name to backup history for",
)
@click.option(
    "--pattern",
    required=False,
    help="Pattern for the resulting timestamped filename, should include an str.format replacement placeholder",
)
@profile
@path
@store_to
@click.pass_context
def save(
    ctx: click.Context,
    browser: Optional[str],
    profile: str,
    to: str,
    path: Optional[str],
    pattern: Optional[str],
) -> None:
    """
    Backs up a current browser database file
    """
    from .save import backup_history, _path_backup

    if path is not None:
        assert pattern is None, "pattern doesn't make sense with path backup"
        _path_backup(path, to)
    elif browser is not None:
        with _wrap_browserexport_cli_errors():
            backup_history(browser, to, profile=profile, pattern=pattern)
    else:
        click.secho(
            "Error: must provide one of '--browser', or '--path'",
            err=True,
            fg="red",
        )
        click.echo(ctx.get_help())


def _handle_merge(dbs: List[str], *, json: bool, stream: bool) -> None:
    from .model import Visit
    from .merge import read_and_merge

    with _wrap_browserexport_cli_errors():
        ivis: Iterator[Visit] = read_and_merge(dbs)
        if json or stream:
            if stream:
                for v in ivis:
                    sys.stdout.write(jsn.dumps(v.serialize()))
                sys.stdout.flush()
            else:
                click.echo(jsn.dumps([v.serialize() for v in ivis]))
        else:
            from .demo import demo_visit

            vis: List[Visit] = list(ivis)
            demo_visit(vis)
            header = f"Use {click.style('vis', fg='green')} to access visit data"

            try:
                import IPython  # type: ignore[import]
            except ModuleNotFoundError:
                click.secho(
                    "You may want to 'python3 -m pip install IPython' for a better REPL experience",
                    fg="yellow",
                )

                import code

                code.interact(local=locals(), banner=header)
            else:
                IPython.embed(header=header)  # type: ignore[no-untyped-call]


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
    with _wrap_browserexport_cli_errors():
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
    with _wrap_browserexport_cli_errors():
        _handle_merge(list(sqlite_db), json=json, stream=stream)


if __name__ == "__main__":
    cli(prog_name="browserexport")
