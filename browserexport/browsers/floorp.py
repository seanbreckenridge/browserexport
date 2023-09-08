from .common import Paths, handle_path, windows_appdata_paths


from .firefox import Firefox


class Floorp(Firefox):
    @classmethod
    def data_directories(cls) -> Paths:
        return handle_path(
            {
                "linux": "~/.floorp",
                "darwin": "~/Library/Application Support/Floorp/Profiles",
                "win32": windows_appdata_paths(r"Floorp/Profiles"),
            },
            browser_name=cls.__name__,
        )
