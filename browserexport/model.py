"""
A namedtuple representaton for the extracted info
"""

from datetime import datetime
from typing import Optional, NamedTuple, Dict, Any


Second = int

# typically isn't used complete by one browser, inludes
# partial information from browsers which supply the information
class Metadata(NamedTuple):
    title: Optional[str] = None
    description: Optional[str] = None
    preview_image: Optional[str] = None
    duration: Optional[Second] = None

    @classmethod
    def make(
        cls,
        title: Optional[str] = None,
        description: Optional[str] = None,
        preview_image: Optional[str] = None,
        duration: Optional[Second] = None,
    ) -> Optional["Metadata"]:
        """
        Alternate constructor; only make the Metadata object if the user
        supplies at least one piece of data
        """
        if (title or description or preview_image or duration) is None:
            return None
        return cls(
            title=title,
            description=description,
            preview_image=preview_image,
            duration=duration,
        )


def test_make_metadata() -> None:
    assert Metadata.make(None, None, None, None) is None
    assert Metadata.make(title="webpage title", duration=5) is not None


class Visit(NamedTuple):
    url: str
    dt: datetime
    # hmm, does this being optional make it more annoying to consume
    # by other programs? reduces the amount of data that other programs
    # need to consume, so theres a tradeoff...
    metadata: Optional[Metadata] = None

    def serialize(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "dt": self.dt.timestamp(),
            "metadata": self.metadata._asdict() if self.metadata is not None else None,
        }
