from typing import Iterator, List, Optional, Type, Any, Dict
from pathlib import Path
from datetime import datetime, timezone

from .common import PathIshOrConn, PathIsh, expand_path
from .model import Visit, Metadata
from .log import logger

from .browsers.common import Browser
from .browsers.all import DEFAULT_BROWSERS


def _read_json_file(path: Path) -> Iterator[Dict[str, Any]]:
    data: List[Dict[str, Any]]
    try:
        # speedup load using orjson if its installed
        import orjson  # type: ignore[import]

        data = orjson.loads(path.read_text())

    except ImportError:
        import json

        data = json.loads(path.read_text())

    yield from data


def _parse_json_file(path: PathIsh) -> Iterator[Visit]:
    for vjson in _read_json_file(expand_path(path)):
        metadata_kwargs = vjson["metadata"] or {}
        yield Visit(
            url=vjson["url"],
            dt=datetime.fromtimestamp(vjson["dt"], tz=timezone.utc),
            metadata=Metadata.make(**metadata_kwargs),
        )


def read_visits(
    path: PathIshOrConn, *, additional_browsers: Optional[List[Type[Browser]]] = None
) -> Iterator[Visit]:
    """
    Takes one sqlite database as input and returns 'Visit's
    """
    browsers: List[Type[Browser]] = additional_browsers or []
    browsers += DEFAULT_BROWSERS
    logger.info(f"Reading visits from {path}...")

    if isinstance(path, (str, Path)) and str(path).endswith(".json"):
        logger.debug("Detected as merged visit JSON dump")
        yield from _parse_json_file(path)
        return
    for br in browsers:
        if br.detect(path):
            logger.debug(f"Detected as {br.__name__}")
            yield from br.extract_visits(path)
            return
    else:
        raise RuntimeError(f"{path} didn't match any known schema")
