import weaviate
from celery import shared_task
from langchain_text_splitters import RecursiveCharacterTextSplitter
from apps.documents.extractors import extract_text
from apps.documents.models import UserDocument
from apps.memory.user_documents import save_document_chunk
from apps.memory.weaviate_client import get_weaviate_client
# ... (your other imports)

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def chunk_and_store_document(self, document_id: int):
    document = UserDocument.objects.get(id=document_id)

    text = extract_text(document.file.path)
    if not text.strip():
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
    )
    chunks = splitter.split_text(text)

    # ----------------------------------------------------
    # OPEN CONNECTION ONCE -> PASS TO FUNCTION
    # ----------------------------------------------------
    with get_weaviate_client() as client:
        for chunk in chunks:
            save_document_chunk(
                client=client,          # <--- Passing the open connection
                text=chunk,
                user_id=document.user_id,
                document_id=document.id,
                session_id=document.session_id,
            )