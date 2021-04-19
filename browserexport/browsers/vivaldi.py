from .common import (
    Path,
    platform,
    _warn_unknown,
)


from .chrome import Chrome


class Vivaldi(Chrome):
    @classmethod
    def data_directory(cls) -> Path:
        p: Path
        if platform == "darwin":
            p = Path("~/Library/Application Support/Vivaldi/")
        else:
            p = Path("~/.config/vivaldi/")
            if platform != "linux":
                _warn_unknown(cls.__name__)
        return p.expanduser()
