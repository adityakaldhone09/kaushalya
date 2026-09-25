from __future__ import annotations
from typing import Any


def success(data: Any) -> dict:
    return {"success": True, "data": data}


def error(code: str, message: str) -> dict:
    return {"success": False, "error": {"code": code, "message": message}}
# dummy change 13
