from .common import (
    Path,
    _handle_path,
)


from .chrome import Chrome


class Vivaldi(Chrome):
    @classmethod
    def data_directory(cls) -> Path:
        return _handle_path(
            {
                "linux": "~/.config/vivaldi/",
                "darwin": "~/Library/Application Support/Vivaldi/",
            },
            browser_name=cls.__name__,
        )
