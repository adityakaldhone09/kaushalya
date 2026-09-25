from __future__ import annotations
from bson import ObjectId
from datetime import datetime


def serialize_doc(doc: dict | None) -> dict | None:
    """Convert MongoDB document to JSON-serializable dict."""
    if doc is None:
        return None
    result = {}
    for k, v in doc.items():
        if k == "_id":
            result["id"] = str(v)
        elif isinstance(v, ObjectId):
            result[k] = str(v)
        elif isinstance(v, datetime):
            result[k] = v.isoformat()
        elif isinstance(v, dict):
            result[k] = serialize_doc(v)
        elif isinstance(v, list):
            result[k] = [
                serialize_doc(i) if isinstance(i, dict)
                else str(i) if isinstance(i, ObjectId)
                else i.isoformat() if isinstance(i, datetime)
                else i
                for i in v
            ]
        else:
            result[k] = v
    return result


def serialize_docs(docs: list[dict]) -> list[dict]:
    return [serialize_doc(d) for d in docs if d is not None]
# dummy change 14
