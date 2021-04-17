from .common import (
    Path,
    platform,
)


from .chrome import Chrome


class Chromium(Chrome):
    @classmethod
    def data_directory(cls) -> Path:
        if platform == "darwin":
            # TODO: figure out where this is on mac
            return Path(".")
        else:
            return Path("~/.config/chromium/").expanduser()
