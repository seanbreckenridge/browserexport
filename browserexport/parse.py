import os
import sqlite3
import tempfile
import shutil
from pathlib import Path
from typing import Iterator, List, Any, Dict, TextIO, Optional, Type, BinaryIO

from kompress import is_compressed, CPath

from .common import PathIshOrConn, PathIsh, expand_path, BrowserexportError
from .model import Visit
from .log import logger

from .browsers.common import Browser
from .browsers.all import DEFAULT_BROWSERS


def _read_json_obj(path: TextIO) -> Iterator[Dict[str, Any]]:
    data: List[Dict[str, Any]]
    try:
        # speedup load using orjson if its installed
        import orjson  # type: ignore[import]

        data = orjson.loads(path.read())

    except ImportError:
        import json

        data = json.loads(path.read())

    yield from data


def _read_json_file(path: PathIsh) -> Iterator[Dict[str, Any]]:
    with expand_path(path).open() as fp:
        yield from _read_json_obj(fp)


def _read_json_lines(fp: TextIO) -> Iterator[Dict[str, Any]]:
    try:
        import orjson  # type: ignore[import]

        for line in fp:
            yield orjson.loads(line)

    except ImportError:
        import json

        for line in fp:
            yield json.loads(line)


JSON_FORMATS = [".json", ".jsonl"]


def _detect_extensions(path: PathIsh) -> str:
    basepath: str = os.path.basename(str(path))
    if is_compressed(basepath):
        basepath, _, _ = basepath.rpartition(".")

    _, primary_ext = os.path.splitext(basepath)
    return primary_ext


def _parse_known_formats(path: PathIsh) -> Iterator[Visit]:
    pth: Path = CPath(expand_path(path))  # type: ignore
    ext = _detect_extensions(path)
    if ext not in JSON_FORMATS:
        raise ValueError(f"Unknown filetype: {path} extension={ext}")
    if ext == ".json":
        yield from map(Visit.from_dict, _read_json_file(pth))
    else:
        assert ext == ".jsonl", f"Unknown extension {ext}"
        logger.debug("Reading as JSON lines")
        with pth.open("r") as fp:
            yield from map(Visit.from_dict, _read_json_lines(fp))


def _read_buf_as_sqlite_db(buf: BinaryIO) -> sqlite3.Connection:
    """
    Reads some binary file object as sqlite database

    Pass sys.stdin.buffer to read from stdin
    """

    dbout = sqlite3.connect(":memory:")

    with tempfile.TemporaryDirectory() as td:
        tfp = Path(tempfile.mktemp(suffix="-browser-buffer.sqlite", dir=td))
        with tfp.open("wb") as tfo:
            logger.debug(f"reading buffer into tempfile {tfp}...")
            shutil.copyfileobj(buf, tfo)

        # copy to an in-memory sqlite database
        logger.debug("copying tempfile to in-memory sqlite database...")
        dbin = sqlite3.connect(str(tfp))

        # backup database, copy to in-memory database so that
        # once the tempfile is deleted, we can still access the data
        dbin.backup(dbout)

        dbin.close()

    assert not tfp.exists(), f"tempfile {tfp} should be deleted, but still exists"
    return dbout


def read_visits(
    path: PathIshOrConn, *, additional_browsers: Optional[List[Type[Browser]]] = None
) -> Iterator[Visit]:
    """
    Takes one sqlite database as input and returns 'Visit's
    """
    browsers: List[Type[Browser]] = additional_browsers or []
    browsers += DEFAULT_BROWSERS
    logger.info(f"Reading visits from {path}...")

    if isinstance(path, (str, Path)) and _detect_extensions(path) in JSON_FORMATS:
        logger.debug("Detected merged JSON file, mapping to Visit directly")
        try:
            yield from _parse_known_formats(path)
            return
        except ValueError as e:
            logger.debug(e, exc_info=True)
            logger.warning(
                f"Failed to parse {path} as known format, trying browsers instead"
            )

    for br in browsers:
        if br.detect(path):
            logger.debug(f"Detected as {br.__name__}")
            yield from br.extract_visits(path)
            return
    else:
        raise BrowserexportError(f"{path} didn't match any known schema")
