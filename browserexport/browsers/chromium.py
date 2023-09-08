from .common import (
    handle_path,
    windows_appdata_paths,
    Paths,
)


from .chrome import Chrome


class Chromium(Chrome):
    @classmethod
    def data_directories(cls) -> Paths:
        return handle_path(
            {
                "linux": (
                    "~/.config/chromium/",
                    "~/.var/app/org.chromium.Chromium/config/chromium/",
                    "~/snap/chromium/common/chromium/",
                ),
                "darwin": "~/Library/Application Support/Chromium/",
                "win32": windows_appdata_paths(r"Chromium\User Data"),
            },
            browser_name=cls.__name__,
        )
