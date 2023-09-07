from .common import Paths, handle_path, windows_appdata_paths


from .chrome import Chrome


# TODO: Opera GX paths here or a separate file?
class Opera(Chrome):
    @classmethod
    def data_directories(cls) -> Paths:
        return handle_path(
            {
                "linux": "~/.config/opera",
                "darwin": "~/Library/Application Support/com.operasoftware.Opera",
                "win32": windows_appdata_paths(r"Opera Software\Opera Stable"),
            },
            browser_name=cls.__name__,
        )
