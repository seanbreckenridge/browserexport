from .common import Paths, handle_path, windows_appdata_paths


from .firefox import Firefox


class Librewolf(Firefox):
    @classmethod
    def data_directories(cls) -> Paths:
        return handle_path(
            {
                "linux": (
                    "~/.librewolf",
                    "~/.var/app/io.gitlab.librewolf-community/.librewolf",
                ),
                "darwin": "~/Library/Application Support/LibreWolf/Profiles",
                "win32": windows_appdata_paths(r"librewolf\Profiles"),
            },
            browser_name=cls.__name__,
        )
