from celery import shared_task
from google import genai

@shared_task
def delete_gemini_file_store(store_name: str):
    """Asynchronously deletes the File Search store from Google Cloud."""
    client = genai.Client()
    try:
        # force=True deletes the store even if it contains documents
        client.file_search_stores.delete(name=store_name, config={'force': True})
        print(f"Successfully deleted File Search store: {store_name}")
    except Exception as e:
        print(f"Failed to delete File Search store {store_name}: {e}")