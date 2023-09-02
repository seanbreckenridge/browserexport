from .common import Paths, handle_path


from .firefox import Firefox


class Floorp(Firefox):
    has_save = True
    has_form_history_save = False

    @classmethod
    def data_directories(cls) -> Paths:
        return handle_path(
            {
                "linux": "~/.floorp",
            },
            browser_name=cls.__name__,
        )
