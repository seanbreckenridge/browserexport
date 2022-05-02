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
    handle_glob,
    handle_path,
    execute_query,
    Paths,
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
        order_by="V.visit_time",
    )

    @classmethod
    def extract_visits(cls, path: PathIshOrConn) -> Iterator[Visit]:
        for row in execute_query(path, cls.schema.query):
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
    def data_directories(cls) -> Paths:
        return handle_path(
            {
                "linux": "~/.config/google-chrome/",
                "darwin": "~/Library/Application Support/Google/Chrome/",
            },
            browser_name=cls.__name__,
        )

    @classmethod
    def locate_database(cls, profile: str = "*") -> Path:
        dd = cls.data_directories()
        return handle_glob(dd, profile + "/History")
