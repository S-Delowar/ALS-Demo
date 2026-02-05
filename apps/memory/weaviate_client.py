import os
import weaviate
from dotenv import load_dotenv
# for local connection (we used docker image)
from weaviate import connect_to_local

load_dotenv()


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


# Connect to Container
# ===============================================
# def get_weaviate_client():
#     """
#     Weaviate v4 client (Docker & Local compatible)
#     """
#     # Docker service name is 'weaviate', but use 'localhost' if running locally
#     host = os.getenv("WEAVIATE_HOST", "weaviate") 
    
#     client = weaviate.connect_to_custom(
#         http_host=host,        # Uses "weaviate" inside Docker
#         http_port=8080,
#         http_secure=False,
#         grpc_host=host,        # Uses "weaviate" inside Docker
#         grpc_port=50051,
#         grpc_secure=False,
#     )
#     return client