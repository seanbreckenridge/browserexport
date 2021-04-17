from .common import (
    Path,
    platform,
    _handle_glob,
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

    @classmethod
    def locate_database(cls, profile: str = "*") -> Path:
        dd: Path = cls.data_directory()
        return _handle_glob(dd, profile + "/History")
