from .common import (
    Path,
    platform,
)
from .firefox import Firefox

# TODO: write extractor, uses a different schema
# uses a similar directory structure to firefox
class Palemoon(Firefox):
    @classmethod
    def data_directory(cls) -> Path:
        if platform == "darwin":
            # TODO: add
            return Path(".")
        else:
            return Path("~/.moonchild productions/pale moon/").expanduser()
