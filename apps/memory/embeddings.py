# from sentence_transformers import SentenceTransformer

# _model = None

# def get_embedding_model():
#     """
#     Loads the model only the first time this function is called.
#     """
#     global _model
#     if _model is None:
#         print("Loading BERT model... (One-time)")
#         _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
#     return _model


# def embed_text(text: str) -> list[float]:
#     """
#     Generate embedding for a single text.
#     """
#     model = get_embedding_model()
#     return model.encode(text).tolist()


import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def embed_text(text:str, task_type: str = "RETRIEVAL_QUERY") -> list[float]:
    try:
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
            config=types.EmbedContentConfig(
                task_type=task_type
            )
        )
        return response.embeddings[0].values 
    except Exception as e:
        print(f"Error embedding text: {e}")
        return []