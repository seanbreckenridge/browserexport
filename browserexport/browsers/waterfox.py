from .common import (
    Path,
    _handle_path
)
from .firefox import Firefox

# seems to match firefox schema well enough for all of our usage
class Waterfox(Firefox):
    @classmethod
    def data_directory(cls) -> Path:
        return _handle_path(
            {
                "linux": "~/.waterfox/",
                "darwin": "~/Library/Application Support/Waterfox/Profiles/",
            },
            browser_name=cls.__name__,
        )
