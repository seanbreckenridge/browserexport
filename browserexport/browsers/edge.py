from os import path

from .common import (
    Paths,
    handle_path,
)

from .chrome import Chrome


class Edge(Chrome):
    @classmethod
    def data_directories(cls) -> Paths:
        return handle_path(
            {
                "win32": path.expandvars("%localappdata%\\Microsoft\\Edge\\"),
            },
            browser_name=cls.__name__,
        )
