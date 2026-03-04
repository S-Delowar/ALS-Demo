# from apps.chatbot.graph.state import ChatState
# from apps.memory.user_documents import search_user_documents
# from apps.memory.weaviate_client import get_weaviate_client


# weaviate_client = get_weaviate_client()

# def document_node(state: ChatState) -> ChatState:
    
#     print("======*********** Document Retrieval Node Called **************======")
    
#     state["documents"] = search_user_documents(
#         query=state["message"],
#         user_id=state["user_id"],
#         session_id=state["session_id"],
#         limit=4,
#         client=weaviate_client,
#     )
    
#     print(f"Output state of Document Retrieval Node: \n\n{state}")
#     print("\n\n====*****End of Document Retrieval Node*****=======")
    
#     return state


import os
import time
from google import genai
from google.genai import types
from ..state import ChatState

# Initialize the new SDK client
client = genai.Client()

def document_node(state: ChatState) -> dict:
    local_file_paths = state.get("local_file_paths", [])
    store_name = state.get("file_search_store_name")
    session_id = state.get("session_id")

    if not local_file_paths:
        return {} # Nothing to upload

    # 1. Create a File Search Store for this session if it doesn't exist
    if not store_name:
        store = client.file_search_stores.create(
            config={'display_name': f'session_{session_id}_store'}
        )
        store_name = store.name

    for path in local_file_paths:
        if os.path.exists(path):
            try:
                # 2. Upload directly to the File Search Store (Chunks and Indexes)
                operation = client.file_search_stores.upload_to_file_search_store(
                    file_search_store_name=store_name,
                    file=path,
                    config={'display_name': os.path.basename(path)}
                )
                
                # 3. Poll for completion as required by the docs
                while not operation.done:
                    time.sleep(2)
                    operation = client.operations.get(operation)
                    
            except Exception as e:
                print(f"Failed to process {path} into File Search: {e}")
            finally:
                # 4. Clean up Django's local temp file
                if os.path.exists(path):
                    os.remove(path)

    # Pass the store name forward so the final LLM can use it as a tool
    return {"file_search_store_name": store_name}




def final_llm_node_document(state: ChatState) -> dict:
    user_message = state.get("message", "")
    history = state.get("history", [])
    store_name = state.get("file_search_store_name")
    
    # 1. Format history for the new SDK
    contents = []
    for msg in history:
        # Map Django DB roles to Gemini roles ('user' or 'model')
        role = "ai" if msg["role"] in ["ai", "assistant", "model"] else "user"
        contents.append(
            types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
        )
    
    # 2. Add current user message
    contents.append(
        types.Content(role="user", parts=[types.Part.from_text(text=user_message)])
    )

    # 3. Configure the File Search Tool if a store exists
    config_kwargs = {}
    if store_name:
        config_kwargs["tools"] = [
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[store_name]
                )
            )
        ]

    try:
        # Use a supported model from the docs (e.g., gemini-2.5-pro or gemini-3-flash-preview)
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=contents,
            config=types.GenerateContentConfig(**config_kwargs) if config_kwargs else None
        )
        final_text = response.text
        
        # Optional: Print grounding metadata to console to see citations during dev
        # print(response.candidates[0].grounding_metadata)
        
    except Exception as e:
        final_text = f"An error occurred during generation: {str(e)}"
            
    return {"final_answer": final_text}