from .common import (
    Iterator,
    Visit,
    Metadata,
    PathIshOrConn,
    Browser,
    unquote,
    platform,
    Path,
    Schema,
    _execute_query,
    _from_datetime_microseconds,
    _func_if_some,
    _handle_glob,
    _warn_unknown,
)


class Firefox(Browser):
    detector = "moz_meta"
    schema = Schema(
        cols=[
            "P.url",
            "V.visit_date",
            "P.title",
            "P.description",
            "P.preview_image_url",
        ],
        where="FROM moz_historyvisits as V, moz_places as P WHERE V.place_id = P.id",
    )

    @classmethod
    def extract_visits(cls, path: PathIshOrConn) -> Iterator[Visit]:
        for row in _execute_query(path, cls.schema.query):
            yield Visit(
                url=unquote(row["url"]),
                dt=_from_datetime_microseconds(row["visit_date"]),
                metadata=Metadata.make(
                    title=row["title"],
                    description=row["description"],
                    preview_image=_func_if_some(row["preview_image_url"], unquote),
                ),
            )

    @classmethod
    def data_directory(cls) -> Path:
        p: Path
        if platform == "darwin":
            p = Path("~/Library/Application Support/Firefox/Profiles/")
        else:
            p = Path("~/.mozilla/firefox/")
            if platform != "linux":
                _warn_unknown(cls.__name__)
        return p.expanduser()

    @classmethod
    def locate_database(cls, profile: str = "*") -> Path:
        dd: Path = cls.data_directory()
        return _handle_glob(dd, profile + "/places.sqlite")
