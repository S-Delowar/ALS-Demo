from sentence_transformers import SentenceTransformer

# Load once (important)
_model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_text(text: str) -> list[float]:
    """
    Generate embedding for a single text.
    """
    return _model.encode(text).tolist()
