import weaviate
from django.conf import settings
from weaviate.exceptions import WeaviateBaseError

# for local connection (we used docker image)
from weaviate import connect_to_local


# _client = None


# def get_weaviate_client():
#     """
#     Singleton Weaviate client with safety checks.
#     """
#     global _client

#     if _client is None:
#         _client = weaviate.Client(
#             url=settings.WEAVIATE_URL,
#             timeout_config=(5, 30),  # (connect_timeout, read_timeout)
#             # additional_headers={},  # no vectorizer API keys
#         )

#         # Optional but STRONGLY recommended
#         try:
#             if not _client.is_ready():
#                 raise RuntimeError("Weaviate is not ready")
#         except WeaviateBaseError as e:
#             raise RuntimeError(
#                 f"Weaviate connection failed: {e}"
#             )

#     return _client


#============================
# Using local connection
def get_weaviate_client():
    """
    Weaviate v4 client (local Docker)
    """
    client = connect_to_local(
        host="localhost",
        port=8080,
        grpc_port=50051,
    )
    return client


# ## Prodcution version (example)

# import os
# import weaviate

# def get_weaviate_client():
#     """
#     Weaviate v4 client
#     - Adapts automatically to Docker (service name) or Localhost
#     """
#     # If running in Docker, this should be "weaviate" (the service name).
#     # If running locally on your laptop, this defaults to "localhost".
#     weaviate_host = os.getenv("WEAVIATE_HOST", "localhost")
#     weaviate_port = int(os.getenv("WEAVIATE_PORT", 8080))
#     weaviate_grpc_port = int(os.getenv("WEAVIATE_GRPC_PORT", 50051))

#     client = weaviate.connect_to_local(
#         host=weaviate_host,
#         port=weaviate_port,
#         grpc_port=weaviate_grpc_port,  # Explicitly set gRPC port
#         # headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")} # Uncomment if using OpenAI module
#     )
    
#     return client