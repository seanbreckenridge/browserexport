from pathlib import Path
from typing import Iterator, List, Any, Dict, TextIO, Optional, Type

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
    with expand_path(path).open("r") as fp:
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


KNOWN_FORMATS = {".json", ".jsonl", ".json.gz", ".jsonl.gz"}


def _is_known_format(path: PathIsh) -> bool:
    pth = expand_path(path)
    return any(pth.name.endswith(ext) for ext in KNOWN_FORMATS)


def _parse_known_formats(path: PathIsh) -> Iterator[Visit]:
    pth = expand_path(path)
    ext = pth.suffix.lower()
    if ext == ".json":
        logger.debug("Reading as JSON")
        yield from map(Visit.from_dict, _read_json_file(pth))
    elif ext == ".jsonl":
        logger.debug("Reading as JSON lines")
        with pth.open("r") as fp:
            yield from map(Visit.from_dict, _read_json_lines(fp))
    elif ext == ".gz":
        import gzip

        if pth.name.endswith(".json.gz"):
            logger.debug("Reading as gzipped JSON")
            with gzip.open(pth, "rt") as fp:
                yield from map(Visit.from_dict, _read_json_obj(fp))
        elif pth.name.endswith(".jsonl.gz"):
            logger.debug("Reading as gzipped JSON lines")
            with gzip.open(path, "rt") as fp:
                yield from map(Visit.from_dict, _read_json_lines(fp))
        else:
            raise ValueError(f"Unknown filetype: {path}")
    else:
        raise ValueError(f"Unknown filetype: {path}")


def read_visits(
    path: PathIshOrConn, *, additional_browsers: Optional[List[Type[Browser]]] = None
) -> Iterator[Visit]:
    """
    Takes one sqlite database as input and returns 'Visit's
    """
    browsers: List[Type[Browser]] = additional_browsers or []
    browsers += DEFAULT_BROWSERS
    logger.info(f"Reading visits from {path}...")

    if isinstance(path, (str, Path)) and _is_known_format(path):
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
