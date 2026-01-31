from requests import session
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.shortcuts import get_object_or_404

from apps.documents.models import UserDocument
from apps.chat.models.session import ChatSession
from apps.documents.tasks import chunk_and_store_document
from apps.memory.user_documents import search_user_documents


# Document upload view
# ===================================================
class UploadDocumentView(APIView):
    """
    Upload a document and (optionally) attach it to a chat session.

    - Saves metadata in PostgreSQL
    - Stores file in MEDIA_ROOT
    - Triggers async chunking + vector storage
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        uploaded_file = request.FILES.get("file")
        session_id = request.data.get("session_id")
        session = None

        if not uploaded_file:
            return Response(
                {"error": "File is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        if session_id:
            session = get_object_or_404(
            ChatSession,
            id=session_id,
            user=request.user
        )

        doc = UserDocument.objects.create(
            user=request.user,
            session=session,
            filename=uploaded_file.name,
            file=uploaded_file
        )
        
        # Async chunking + vector store
        chunk_and_store_document.delay(doc.id)

        return Response(
            {
                "id": doc.id,
                "filename": doc.filename,
                "session_id": session.id if session else None,
                "status": "uploaded",
            },
            status=status.HTTP_201_CREATED,
        )


# Search documents view
# ===================================================
class SearchDocumentsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        
        query = request.data.get("query")
        
        session_id = request.data.get("session_id")
        
        user_id = request.user.id
        
        # Perform vector search using Weaviate client
        results = search_user_documents(
            query=query, 
            user_id=user_id,
            session_id=session_id
        )
        
        return Response(
            {
                "results": results
            },
            status=status.HTTP_200_OK,
        )