from __future__ import annotations
"""
Embeddings using Gemini text-embedding-004.
Falls back gracefully when unavailable.
"""
import logging
from .gemini_client import get_client

logger = logging.getLogger(__name__)
EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIM = 768


def get_embedding(text: str) -> list[float]:
    """Generate embedding for text. Returns [] on failure."""
    c = get_client()
    if c is None:
        return []
    try:
        response = c.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
        )
        # SDK 1.x: response.embeddings is a list of EmbedContentResponse
        embs = getattr(response, "embeddings", None)
        if embs and len(embs) > 0:
            values = getattr(embs[0], "values", None)
            if values:
                return list(values)
        # Alternative path
        if hasattr(response, "embedding"):
            return list(response.embedding.values)
        return []
    except Exception as exc:
        logger.warning("Embedding failed: %s", exc)
        return []


def embeddings_available() -> bool:
    return get_client() is not None
