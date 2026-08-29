from .embeddings import get_embedding

def vector_search(query: str, top_k: int = 5):
    # Dummy implementation for vector search
    query_emb = get_embedding(query)
    return [{"text": "Mock retrieved document", "score": 0.9}]
