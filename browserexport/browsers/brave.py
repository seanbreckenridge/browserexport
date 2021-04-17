from .common import (
    Path,
    platform,
    _handle_glob,
)


from .chrome import Chrome


class Brave(Chrome):
    @classmethod
    def data_directory(cls) -> Path:
        if platform == "darwin":
            # TODO: figure out where this is on mac
            return Path(".")
        else:
            return Path("~/.config/BraveSoftware/Brave-Browser/").expanduser()
