from sentence_transformers import SentenceTransformer

_model = None

def get_embedding_model():
    """
    Loads the model only the first time this function is called.
    """
    global _model
    if _model is None:
        print("Loading BERT model... (One-time)")
        _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return _model


def embed_text(text: str) -> list[float]:
    """
    Generate embedding for a single text.
    """
    model = get_embedding_model()
    return model.encode(text).tolist()