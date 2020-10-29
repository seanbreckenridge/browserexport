from os import environ
import logging
from logzero import setup_logger  # type: ignore[import]

# https://docs.python.org/3/library/logging.html#logging-levels
loglevel: int = logging.WARNING  # (30)
if "FFEXPORT_LOGS" in environ:
    loglevel = int(environ["FFEXPORT_LOGS"])

# logzero handles this fine, can be imported/configured
# multiple times
logger = setup_logger(name="ffexport", level=loglevel)
