from .common import Path, handle_path


from .chrome import Chrome


class Brave(Chrome):
    @classmethod
    def data_directory(cls) -> Path:
        return handle_path(
            {
                "linux": "~/.config/BraveSoftware/Brave-Browser/",
                "darwin": "~/Library/Application Support/BraveSoftware/Brave-Browser/",
            },
            browser_name=cls.__name__,
        )
