from .common import (
    Path,
    Schema,
    platform,
    Iterator,
    Visit,
    unquote,
    _from_datetime_microseconds,
    _execute_query,
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
                visit_date=_from_datetime_microseconds(row["visit_date"]),
                title=row["title"],
            )

    @classmethod
    def data_directory(cls) -> Path:
        if platform == "darwin":
            # TODO: add
            return Path(".")
        else:
            return Path("~/.moonchild productions/pale moon/").expanduser()
