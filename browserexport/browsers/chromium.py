from .common import (
    Path,
    handle_path,
)


from .chrome import Chrome


class Chromium(Chrome):
    @classmethod
    def data_directory(cls) -> Path:
        return handle_path(
            {
                "linux": "~/.config/chromium/",
                "darwin": "~/Library/Application Support/Chromium/",
            },
            browser_name=cls.__name__,
        )
