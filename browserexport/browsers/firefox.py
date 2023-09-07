from typing import TypeVar, Callable
from urllib.parse import unquote

from .common import (
    Iterator,
    Visit,
    Optional,
    Metadata,
    PathIshOrConn,
    Browser,
    Path,
    windows_appdata_paths,
    Schema,
    execute_query,
    from_datetime_microseconds,
    handle_glob,
    handle_path,
    Paths,
)

T = TypeVar("T")


def func_if_some(maybe: Optional[T], func: Callable[[T], T]) -> Optional[T]:
    """if 'maybe' is not None, run the specified function"""
    if maybe is not None:
        return func(maybe)
    return maybe


class Firefox(Browser):
    detector = "SELECT * FROM moz_meta, moz_annos"
    schema = Schema(
        cols=[
            "P.url",
            # Hack to tell apart whether timestamp is stored in microseconds (on desktop) or in milliseconds (on mobile)
            # We set 300_000_000 as threshold, it's year 1979, so definitely before Firefox existed,
            # and the same multipied by 1000 is year 11476, also enough time for us not to care.
            "(CASE WHEN (V.visit_date > 300000000 * 1000000) THEN V.visit_date ELSE V.visit_date * 1000 END) AS visit_date",
            "V.visit_date",
            "P.title",
            "P.description",
            "P.preview_image_url",
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
                metadata=Metadata.make(
                    title=row["title"],
                    description=row["description"],
                    preview_image=func_if_some(row["preview_image_url"], unquote),
                ),
            )

    @classmethod
    def data_directories(cls) -> Paths:
        return handle_path(
            {
                "linux": (
                    "~/.mozilla/firefox/",
                    "~/.var/app/org.mozilla.firefox/.mozilla/firefox/",
                    "~/snap/firefox/common/.mozilla/firefox/",
                ),
                "darwin": "~/Library/Application Support/Firefox/Profiles/",
                "win32": windows_appdata_paths("Mozilla/Firefox/Profiles/"),
            },
            browser_name=cls.__name__,
        )

    @classmethod
    def locate_database(cls, profile: str = "*") -> Path:
        dd = cls.data_directories()
        return handle_glob(dd, profile + "/places.sqlite")
