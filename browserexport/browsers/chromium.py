from .common import (
    handle_path,
    Paths,
)


from .chrome import Chrome


class Chromium(Chrome):
    @classmethod
    def data_directories(cls) -> Paths:
        return handle_path(
            {
                "linux": ("~/.config/chromium/", "~/snap/chromium/common/chromium/"),
                "darwin": "~/Library/Application Support/Chromium/",
            },
            browser_name=cls.__name__,
        )
