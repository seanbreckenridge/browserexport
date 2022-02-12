from .common import (
    Iterator,
    Visit,
    Metadata,
    PathIshOrConn,
    Browser,
    unquote,
    Path,
    Schema,
    _execute_query,
    _from_datetime_microseconds,
)


class FirefoxMobileLegacy(Browser):
    detector = "remote_devices"
    schema = Schema(
        cols=[
            "H.url",
            "V.date",
            "H.title",
        ],
        where="FROM visits as V, history as H WHERE V.history_guid = H.guid",
        # todo: bookmarks, searchhistory tables might be interesting
    )

    @classmethod
    def extract_visits(cls, path: PathIshOrConn) -> Iterator[Visit]:
        for row in _execute_query(path, cls.schema.query):
            yield Visit(
                url=unquote(row["url"]),
                dt=_from_datetime_microseconds(row["date"]),
                metadata=Metadata.make(
                    title=row["title"],
                ),
            )

    @classmethod
    def data_directory(cls) -> Path:
        raise NotImplementedError("Only available on Android")

    @classmethod
    def locate_database(cls, profile: str) -> Path:
        raise NotImplementedError("Only available on Android")
