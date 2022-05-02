from .common import Paths, handle_path


from .chrome import Chrome


class Brave(Chrome):
    @classmethod
    def data_directories(cls) -> Paths:
        return handle_path(
            {
                "linux": "~/.config/BraveSoftware/Brave-Browser/",
                "darwin": "~/Library/Application Support/BraveSoftware/Brave-Browser/",
            },
            browser_name=cls.__name__,
        )
