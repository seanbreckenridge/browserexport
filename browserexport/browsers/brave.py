from .common import (
    Path,
    platform,
    _warn_unknown,
)


from .chrome import Chrome


class Brave(Chrome):
    @classmethod
    def data_directory(cls) -> Path:
        p: Path
        if platform == "darwin":
            p = Path("~/Library/Application Support/BraveSoftware/Brave-Browser/")
        else:
            p = Path("~/.config/BraveSoftware/Brave-Browser/").expanduser()
            if platform != "linux":
                _warn_unknown(cls.__name__)
        return p.expanduser()
