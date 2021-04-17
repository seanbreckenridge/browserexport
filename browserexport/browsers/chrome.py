from .common import (
    Iterator,
    Visit,
    PathIshOrConn,
    Browser,
    Optional,
    unquote,
    platform,
    Path,
    datetime,
    timezone,
    _execute_query,
    _handle_glob,
)

WINDOWS_EPOCH_OFFSET = 11644473600


def _chrome_date_to_utc(chrome_time: int) -> datetime:
    epoch = (chrome_time / 1_000_000) - WINDOWS_EPOCH_OFFSET
    return datetime.fromtimestamp(epoch, tz=timezone.utc)


class Chrome(Browser):
    detector = "keyword_search_terms"

    query = """SELECT U.url, V.visit_time, U.title
FROM visits as V, urls as U
WHERE V.url = U.id"""

    @classmethod
    def extract_visits(cls, path: PathIshOrConn) -> Iterator[Visit]:
        for row in _execute_query(path, cls.query):
            yield Visit(
                url=row["url"],
                visit_date=_chrome_date_to_utc(row["visit_time"]),
                title=row["title"],
            )

    @classmethod
    def data_directory(cls) -> Path:
        if platform == "darwin":
            # TODO: figure out where this is on mac
            return Path(".")
        else:
            return Path("~/.config/google-chrome/").expanduser()

    @classmethod
    def locate_database(cls, profile: str = "*") -> Path:
        dd: Path = cls.data_directory()
        return _handle_glob(dd, profile + "/History")
