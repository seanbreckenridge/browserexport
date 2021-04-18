from .common import (
    Path,
    platform,
    _warn_unknown,
)
from .firefox import Firefox

# seems to match firefox schema well enough for all of our usage
class Waterfox(Firefox):
    @classmethod
    def data_directory(cls) -> Path:
        p: Path
        if platform == "darwin":
            p = Path("~/Library/Application Support/Waterfox/Profiles/")
        else:
            p = Path("~/.waterfox/")
            if platform != "linux":
                _warn_unknown(cls.__name__)
        return p.expanduser()
