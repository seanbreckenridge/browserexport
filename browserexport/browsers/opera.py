from typing import Optional
from .common import (
    BrowserexportError,
    Paths,
    handle_path,
    windows_appdata_paths,
    handle_glob,
    Path,
)


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

    @classmethod
    def locate_database(cls, profile: str = "*") -> Path:
        # on linux, this seems to be just flat in ~/.config/opera without a 'Default' folder
        # like the typical chromium browsers. While on windows, its in the 'Default' folder like Chrome
        # can try both and see which works
        dd = cls.data_directories()
        err: Optional[BrowserexportError] = None
        # the '/' here allows the user to specify a profile name to disambiguate
        # but also makes it so it checks the base path + a subdir
        #
        # e.g. it checks:
        # ~/.config/opera/*/History
        # then
        # ~/.config/opera/*History
        #
        # If the user provides a profile name, it checks:
        # ~/.config/opera/ProfileName*/History
        # then
        # ~/.config/opera/*History
        for pth in ("/History", "History"):
            try:
                return handle_glob(dd, profile + pth)
            except BrowserexportError as e:
                if err is None:
                    err = e

        assert err is not None
        raise err
