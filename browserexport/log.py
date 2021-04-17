"""
Setup logging for this module
"""

import os
import logging

from typing import Optional

from logzero import setup_logger  # type: ignore[import]

DEFAULT_LEVEL = logging.WARNING

# global access to the logger
logger: logging.Logger


# logzero handles adding handling/modifying levels fine
# can be imported/configured multiple times
def setup(level: Optional[int] = None) -> logging.Logger:
    chosen_level = level or int(os.environ.get("BROWSEREXPORT_LOGS", DEFAULT_LEVEL))
    lgr: logging.Logger = setup_logger(name=__package__, level=chosen_level)
    return lgr


# runs the first time this file is run, setup can be imported/run multiple times in other places
logger = setup()
