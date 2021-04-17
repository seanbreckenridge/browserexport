from .common import (
    Path,
    platform,
    _warn_unknown,
)


from .chrome import Chrome


class Brave(Chrome):
    @classmethod
    def data_directory(cls) -> Path:
        p = Path("~/.config/BraveSoftware/Brave-Browser/").expanduser()
        if platform != "linux":
            _warn_unknown(cls.__name__, p)
        return p
