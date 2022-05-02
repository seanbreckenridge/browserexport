from .common import (
    Iterator,
    Visit,
    Metadata,
    PathIshOrConn,
    Browser,
    unquote,
    Path,
    Schema,
    execute_query,
    from_datetime_microseconds,
    Paths,
)


class FirefoxMobileLegacy(Browser):
    """
    Legacy format, used on Android pre-2020.
    The DB was at /data/data/org.mozilla.firefox/files/places.sqlite
    """

    detector = "remote_devices"
    schema = Schema(
        cols=[
            "H.url",
            "V.date",
            "H.title",
        ],
        where="FROM visits as V, history as H WHERE V.history_guid = H.guid",
        order_by="V.date",
        # todo: bookmarks, searchhistory tables might be interesting
    )
    has_save = False

    @classmethod
    def extract_visits(cls, path: PathIshOrConn) -> Iterator[Visit]:
        for row in execute_query(path, cls.schema.query):
            yield Visit(
                url=unquote(row["url"]),
                dt=from_datetime_microseconds(row["date"]),
                metadata=Metadata.make(
                    title=row["title"],
                ),
            )

    @classmethod
    def data_directories(cls) -> Paths:
        raise NotImplementedError("Only available on Android")

    @classmethod
    def locate_database(cls, profile: str = "*") -> Path:
        raise NotImplementedError("Only available on Android")
