from .common import Paths, handle_path


from .firefox import Firefox


class Librewolf(Firefox):
    has_save = True
    has_form_history_save = False

    @classmethod
    def data_directories(cls) -> Paths:
        return handle_path(
            {
                "linux": (
                    "~/.librewolf",
                    "~/.var/app/io.gitlab.librewolf-community/.librewolf",
                ),
                "darwin": "~/.librewolf",
            },
            browser_name=cls.__name__,
        )
