from .common import (
    Path,
    Schema,
    platform,
    Iterator,
    Visit,
    Metadata,
    unquote,
    _from_datetime_microseconds,
    _execute_query,
    _warn_unknown,
    PathIshOrConn,
)
from .firefox import Firefox

# uses a similar directory structure to firefox
class Palemoon(Firefox):
    # only major difference seems to be it doesn't have
    # the 'moz_meta' table? everyhing else is similar
    # to firefox schema
    detector = "moz_historyvisits"

    # seems to store less info that firefox schema
    # no description or preview_image
    schema = Schema(
        cols=[
            "P.url",
            "V.visit_date",
            "P.title",
        ],
        where="FROM moz_historyvisits as V, moz_places as P WHERE V.place_id = P.id",
    )

    @classmethod
    def extract_visits(cls, path: PathIshOrConn) -> Iterator[Visit]:
        for row in _execute_query(path, cls.schema.query):
            yield Visit(
                url=unquote(row["url"]),
                dt=_from_datetime_microseconds(row["visit_date"]),
                metadata=Metadata.make(title=row["title"]),
            )

    # seems the non-linux community is pretty small?
    # https://forum.palemoon.org/viewforum.php?f=41
    # no easy to way to install except to build from source
    # if someone is actually using this on mac, feel free to make an issue
    @classmethod
    def data_directory(cls) -> Path:
        p = Path("~/.moonchild productions/pale moon/")
        if platform != "linux":
            _warn_unknown(cls.__name__)
        return p.expanduser()
