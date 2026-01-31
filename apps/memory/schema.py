import weaviate.classes.config as wvc
from .weaviate_client import get_weaviate_client

def create_schema():
    with get_weaviate_client() as client:
        # 1. GlobalActivities
        if not client.collections.exists("GlobalActivities"):
            client.collections.create(
                name="GlobalActivities",
                vector_config=wvc.Configure.Vectorizer.none(),
                properties=[
                    wvc.Property(name="text", data_type=wvc.DataType.TEXT),
                    wvc.Property(name="profession", data_type=wvc.DataType.TEXT),
                    wvc.Property(name="version", data_type=wvc.DataType.TEXT),
                ]
            )

        # 2. PersonaMemory
        if not client.collections.exists("PersonaMemory"):
            client.collections.create(
                name="PersonaMemory",
                vector_config=wvc.Configure.Vectorizer.none(),
                properties=[
                    wvc.Property(name="text", data_type=wvc.DataType.TEXT),
                    wvc.Property(name="user_id", data_type=wvc.DataType.INT),
                    wvc.Property(name="confidence", data_type=wvc.DataType.NUMBER),
                    wvc.Property(name="type", data_type=wvc.DataType.TEXT),
                ]
            )

        # 3. UserDocuments
        if not client.collections.exists("UserDocuments"):
            client.collections.create(
                name="UserDocuments",
                vector_config=wvc.Configure.Vectorizer.none(),
                properties=[
                    wvc.Property(name="text", data_type=wvc.DataType.TEXT),
                    wvc.Property(name="user_id", data_type=wvc.DataType.INT),
                    wvc.Property(name="session_id", data_type=wvc.DataType.INT),
                    wvc.Property(name="document_id", data_type=wvc.DataType.INT),
                ]
            )