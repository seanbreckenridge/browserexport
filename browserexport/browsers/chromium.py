from .common import (
    Path,
    platform,
    _warn_unknown,
)


from .chrome import Chrome


class Chromium(Chrome):
    @classmethod
    def data_directory(cls) -> Path:
        p: Path
        if platform == "darwin":
            p = Path("~/Library/Application Support/Chromium/")
        else:
            p = Path("~/.config/chromium/")
            if platform != "linux":
                _warn_unknown(cls.__name__)
        return p.expanduser()
