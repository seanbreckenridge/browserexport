"""
A namedtuple representaton for the extracted info
"""

from datetime import datetime
from typing import Optional, NamedTuple, Dict, Any


class Visit(NamedTuple):
    url: str
    visit_date: datetime
    title: Optional[str] = None
    description: Optional[str] = None
    preview_image: Optional[str] = None

    def serialize(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "visit_date": self.visit_date.timestamp(),
            "title": self.title,
            "description": self.description,
            "preview_image": self.preview_image,
        }
