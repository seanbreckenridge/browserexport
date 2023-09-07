from .common import (
    Paths,
    handle_path,
    windows_appdata_paths,
)

from .chrome import Chrome


class Edge(Chrome):
    @classmethod
    def data_directories(cls) -> Paths:
        return handle_path(
            {
                "win32": windows_appdata_paths(r"Microsoft\Edge"),
            },
            browser_name=cls.__name__,
        )
