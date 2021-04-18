from typing import Iterator, List, Optional, Type

from .common import PathIshOrConn
from .model import Visit
from .log import logger

from .browsers.common import Browser
from .browsers.all import DEFAULT_BROWSERS


def read_visits(
    path: PathIshOrConn, *, additional_browsers: Optional[List[Type[Browser]]] = None
) -> Iterator[Visit]:
    """
    Takes one sqlite database as input and returns 'Visit's
    """
    browsers: List[Type[Browser]] = additional_browsers or []
    browsers += DEFAULT_BROWSERS
    logger.info(f"Reading visits from {path}...")
    for br in browsers:
        if br.detect(path):
            logger.debug(f"Detected as {br.__name__}")
            yield from br.extract_visits(path)
            return
    else:
        raise RuntimeError(f"{path} didn't match any known schema")
