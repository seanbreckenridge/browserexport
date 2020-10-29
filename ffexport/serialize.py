from typing import Dict, Any

from .model import MozVisit, MozPlace, Visit


def serialize_moz_visit(mv: MozVisit) -> Dict[str, Any]:
    return {
        "url": mv.url,
        "place_id": mv.place_id,
        "visit_id": mv.visit_id,
        "visit_date": int(mv.visit_date.timestamp()),
        "visit_type": mv.visit_type,
    }


def serialize_moz_place(mp: MozPlace) -> Dict[str, Any]:
    return {
        "place_id": mp.place_id,
        "title": mp.title,
        "description": mp.description,
        "preview_image": mp.preview_image,
    }


def serialize_visit(vs: Visit) -> Dict[str, Any]:
    return {
        "url": vs.url,
        "visit_date": int(vs.visit_date.timestamp()),
        "visit_type": vs.visit_type,
        "title": vs.title,
        "description": vs.description,
        "preview_image": vs.preview_image,
    }
