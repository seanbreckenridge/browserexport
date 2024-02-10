from browserexport.model import test_make_metadata
from browserexport.parse import _detect_extensions


def test_detect_extensions() -> None:
    assert _detect_extensions("foo.json") == ".json"
    assert _detect_extensions("foo.json.gz") == ".json"
    assert _detect_extensions("foo.jsonl") == ".jsonl"
    assert _detect_extensions("foo.jsonl.gz") == ".jsonl"
    assert _detect_extensions("/something/else/foo.sqlite") == ".sqlite"
    assert _detect_extensions("/something/else/foo.jsonl.gz") == ".jsonl"
    assert _detect_extensions("/something/else/foo.jsonl.zstd") == ".jsonl"
    assert _detect_extensions("/something/else/foo.jsonl.xz") == ".jsonl"
