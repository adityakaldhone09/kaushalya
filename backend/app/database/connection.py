from __future__ import annotations

import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config.settings import get_settings

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def _make_client(uri: str, db_name: str) -> tuple[AsyncIOMotorClient, AsyncIOMotorDatabase]:
    """Create a Motor client, injecting certifi CA bundle for Atlas TLS on Python 3.9/macOS."""
    kwargs: dict = {
        "serverSelectionTimeoutMS": 8000,
        "connectTimeoutMS": 8000,
    }
    # Python 3.9 on macOS ships with LibreSSL which breaks Atlas TLS.
    # Inject certifi's CA bundle to fix it.
    if "+srv" in uri or "mongodb.net" in uri:
        try:
            import certifi
            kwargs["tlsCAFile"] = certifi.where()
        except ImportError:
            pass

    client = AsyncIOMotorClient(uri, **kwargs)
    db = client[db_name]
    return client, db


async def connect_db() -> None:
    global _client, _db
    settings = get_settings()
    try:
        _client, _db = _make_client(settings.MONGODB_URI, settings.MONGODB_DB_NAME)
        await _client.admin.command("ping")
        logger.info("MongoDB connected — database: %s", settings.MONGODB_DB_NAME)
    except Exception as exc:
        logger.error("MongoDB connection failed: %s", exc)
        raise


async def close_db() -> None:
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        logger.info("MongoDB connection closed")


def get_db() -> AsyncIOMotorDatabase:
    """Return DB instance; auto-reconnect lazy if the global is missing."""
    global _client, _db
    if _db is not None:
        return _db
    settings = get_settings()
    _client, _db = _make_client(settings.MONGODB_URI, settings.MONGODB_DB_NAME)
    return _db


async def check_db_health() -> bool:
    try:
        if _client is None:
            return False
        await _client.admin.command("ping")
        return True
    except Exception:
        return False
