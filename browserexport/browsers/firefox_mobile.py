from .common import Path, Paths


from .firefox import Firefox


class FirefoxMobile(Firefox):
    """
    New format, used on Android since 2020.
    The DB for stable Firefox is at /data/data/org.mozilla.firefox/files/places.sqlite
    The DB for Fenix is at /data/data/org.mozilla.fenix/files/places.sqlite

    Note that currently the DB schema seems more or less identical, except for timestamps:
    they are in microseconds on desktop and in milliseconds on mobile.
    This is handled in base Firefox class for both cases.
    """

    has_form_history_save = False

    # unclear how reliable it is
    # but we prefer to set it anyway to tell apart whether visits came from desktop or mobile
    # see https://github.com/seanbreckenridge/browserexport/issues/14#issuecomment-1037891476
    detector = "SELECT * FROM moz_meta, moz_tags"
    has_save = False

    @classmethod
    def data_directories(cls) -> Paths:
        raise NotImplementedError("Only available on Android")

    @classmethod
    def locate_database(cls, profile: str = "*") -> Path:
        raise NotImplementedError("Only available on Android")
