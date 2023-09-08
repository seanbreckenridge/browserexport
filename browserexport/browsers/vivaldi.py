from .common import (
    Paths,
    handle_path,
    windows_appdata_paths,
)


from .chrome import Chrome


class Vivaldi(Chrome):
    @classmethod
    def data_directories(cls) -> Paths:
        return handle_path(
            {
                "linux": "~/.config/vivaldi/",
                "darwin": "~/Library/Application Support/Vivaldi/",
                "win32": windows_appdata_paths(r"Vivaldi\User Data"),
            },
            browser_name=cls.__name__,
        )
