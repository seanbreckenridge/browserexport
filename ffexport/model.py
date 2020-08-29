"""
A namedtuple representaton for the extracted info
"""

from datetime import datetime
from typing import Optional, NamedTuple

# MozVisit and MozPlace represent the correspoding rows from
# a single sqlite database

StrMetadata = Optional[str]


class MozVisit(NamedTuple):
    url: str
    place_id: int
    visit_id: int
    visit_date: datetime
    visit_type: int


class MozPlace(NamedTuple):
    place_id: int
    title: StrMetadata
    description: StrMetadata
    preview_image: StrMetadata


# Visit combines MozVisit and MozPlace, removing (possibly? not sure)
# database-specific IDs, leaving the data (url, date, type, any StrMetadata)
# This also means its fine to merge firefox histories from different computers,
# as this isnt using any surrogate keys, its just the data

# Is a bit inefficient, as were duplicating a bunch of metadata across
# visits, but I feel thats convenient enough to do that its worth it
# could also do @property or save _moz_place on the namedtuple itself,
# but that might mess with future cachew usage


class Visit(NamedTuple):
    url: str
    visit_date: datetime
    visit_type: int
    title: StrMetadata
    description: StrMetadata
    preview_image: StrMetadata
