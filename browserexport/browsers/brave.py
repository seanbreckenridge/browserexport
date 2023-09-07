from .common import Paths, handle_path, windows_appdata_paths


from .chrome import Chrome


class Brave(Chrome):
    @classmethod
    def data_directories(cls) -> Paths:
        return handle_path(
            {
                "linux": (
                    "~/.config/BraveSoftware/Brave-Browser/",
                    "~/.var/app/com.brave.Browser/config/BraveSoftware/Brave-Browser/",
                ),
                "darwin": "~/Library/Application Support/BraveSoftware/Brave-Browser/",
                "win32": windows_appdata_paths(
                    r"BraveSoftware\Brave-Browser\User Data"
                ),
            },
            browser_name=cls.__name__,
        )
