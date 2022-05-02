from .common import (
    Path,
    Schema,
    Iterator,
    Visit,
    Browser,
    Metadata,
    unquote,
    from_datetime_microseconds,
    execute_query,
    handle_path,
    handle_glob,
    Paths,
    PathIshOrConn,
    sqlite3,
    logger,
)


class Palemoon(Browser):
    """
    uses a similar directory structure to firefox,
    but has enough things different that worth subclassing Browser
    """

    detector = "moz_historyvisits"

    @classmethod
    def detect(cls, path: PathIshOrConn) -> bool:
        # if this doesnt have the moz_historyvisits, exit
        if not super().detect(path):
            return False
        try:
            # Palemoon doesn't have the moz_meta table, so can use that
            # to make sure this is palemoon and not some other firefox derivative?
            logger.debug(
                "May be Palemoon, running query on moz_meta to ensure this isn't another Firefox derivative"
            )
            list(execute_query(path, "Select * FROM moz_meta"))
            logger.debug("'moz_meta' query failed, not Palemoon")
            return False
        except sqlite3.OperationalError:
            logger.debug(
                "moz_historyvisits exists but moz_meta doesn't, detected as Palemoon"
            )
            return True

    # seems to store less info that firefox schema
    # no description or preview_image
    schema = Schema(
        cols=[
            "P.url",
            "V.visit_date",
            "P.title",
        ],
        where="FROM moz_historyvisits as V, moz_places as P WHERE V.place_id = P.id",
        order_by="V.visit_date",
    )

    @classmethod
    def extract_visits(cls, path: PathIshOrConn) -> Iterator[Visit]:
        for row in execute_query(path, cls.schema.query):
            yield Visit(
                url=unquote(row["url"]),
                dt=from_datetime_microseconds(row["visit_date"]),
                metadata=Metadata.make(title=row["title"]),
            )

    # seems the non-linux community is pretty small?
    # https://forum.palemoon.org/viewforum.php?f=41
    # no easy to way to install except to build from source
    # if someone is actually using this on mac, feel free to make an issue
    @classmethod
    def data_directories(cls) -> Paths:
        return handle_path(
            {
                "linux": "~/.moonchild productions/pale moon/",
            },
            browser_name=cls.__name__,
        )

    @classmethod
    def locate_database(cls, profile: str = "*") -> Path:
        dd = cls.data_directories()
        return handle_glob(dd, profile + "/places.sqlite")
