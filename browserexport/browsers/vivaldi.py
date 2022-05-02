from .common import (
    Paths,
    handle_path,
)


from .chrome import Chrome


class Vivaldi(Chrome):
    @classmethod
    def data_directories(cls) -> Paths:
        return handle_path(
            {
                "linux": "~/.config/vivaldi/",
                "darwin": "~/Library/Application Support/Vivaldi/",
            },
            browser_name=cls.__name__,
        )
