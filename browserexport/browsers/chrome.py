from .common import (
    Iterator,
    Visit,
    Metadata,
    PathIshOrConn,
    Browser,
    unquote,
    Schema,
    Path,
    datetime,
    timezone,
    _execute_query,
    _handle_glob,
    _handle_path,
)

WINDOWS_EPOCH_OFFSET = 11644473600


def _chrome_date_to_utc(chrome_time: int) -> datetime:
    ts = (chrome_time / 1_000_000) - WINDOWS_EPOCH_OFFSET
    return datetime.fromtimestamp(ts, tz=timezone.utc)


class Chrome(Browser):
    detector = "keyword_search_terms"

    schema = Schema(
        cols=[
            "U.url",
            "U.title",
            "V.visit_time",
            "V.visit_duration",
        ],
        where="FROM visits as V, urls as U WHERE V.url = U.id",
    )

    @classmethod
    def extract_visits(cls, path: PathIshOrConn) -> Iterator[Visit]:
        for row in _execute_query(path, cls.schema.query):
            dur = int(row["visit_duration"])
            yield Visit(
                url=unquote(row["url"]),
                dt=_chrome_date_to_utc(row["visit_time"]),
                metadata=Metadata.make(
                    title=row["title"],
                    duration=None if dur == 0 else dur // 1_000_000,
                ),
            )

    @classmethod
    def data_directory(cls) -> Path:
        return _handle_path(
            {
                "linux": "~/.config/google-chrome/",
                "darwin": "~/Library/Application Support/Google/Chrome/",
            },
            browser_name=cls.__name__,
        )


    @classmethod
    def locate_database(cls, profile: str = "*") -> Path:
        dd: Path = cls.data_directory()
        return _handle_glob(dd, profile + "/History")
