from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.core.files.storage import FileSystemStorage


from apps.chat.models import ChatSession, ChatMessage
from apps.persona.services import ChatProfilerTriggerService, check_and_trigger_persona_update
from apps.user_profile.models import UserProfile
from .serializers import ChatSessionSerializer, ChatMessageSerializer


class CreateChatSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """List chat sessions for the current user."""
        sessions = ChatSession.objects.filter(user=request.user).order_by("-updated_at")
        return Response(ChatSessionSerializer(sessions, many=True).data)

    def post(self, request):
        session = ChatSession.objects.create(
            user=request.user,
        )
        return Response(ChatSessionSerializer(session).data)


class ChatSessionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, session_id):
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        session.delete()
        return Response(status=204)


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, session_id):
        session = get_object_or_404(
            ChatSession,
            id=session_id,
            user=request.user
        )

        content = request.data["message"]

        message = ChatMessage.objects.create(
            session=session,
            role="user",
            content=content
        )

        # 🔥 Auto-title logic (only once)
        if session.title == "New chat":
            session.title = content[:60]  # safe truncation
            session.save(update_fields=["title"])

        # Background Task
        # Check Persona Trigger
        check_and_trigger_persona_update(
            session=session, 
            user=request.user
        )

        return Response(ChatMessageSerializer(message).data)



class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session = get_object_or_404(
            ChatSession,
            id=session_id,
            user=request.user
        )


        messages = session.messages.all()
        return Response(ChatMessageSerializer(messages, many=True).data)


# ==========================================
# ==========================================
# CHstbot API View
from apps.chatbot.graph.graph import chatbot_graph


class ChatbotAPIView(APIView):
    permission_classes = [IsAuthenticated]
    # Accept multipart form data 
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request, session_id):
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        message_content = request.data.get("message")

        if not message_content:
            return Response({"error": "Message content is required"}, status=400)

        # Extracts and temporarily save uploaded files
        uploaded_files = request.FILES.getlist("files")
        local_file_paths = []
        
        if uploaded_files:
            fs = FileSystemStorage(location="temp/chat_uploads/")
            for f in uploaded_files:
                filename = fs.save(f.name, f)
                local_file_paths.append(fs.path(filename))

        # Save User Message to DB
        ChatMessage.objects.create(
            session=session,
            role="user",
            content=message_content,
        )

        # Fetch History (Includes the message just created)
        # We fetch the last 10 messages to keep context window efficient
        history_queryset = session.messages.order_by("-created_at")[:10]
        history = list(history_queryset.values("role", "content"))[::-1]  #Reverse - oldest first


        store_name = session.file_search_store_name

        # Prepare State for LangGraph/StateGraph
        state = {
            "user_id": request.user.id,
            "session_id": session.id,
            "message": message_content,
            "history": history,
            "intent": "",       # specific keys required by your ChatState
            "final_answer": None,
            "local_file_paths": local_file_paths,
            "file_search_store_name": store_name
        }

        # Invoke the Graph
        result = chatbot_graph.invoke(state)
        final_answer = result.get("final_answer", "No response generated.")
        
        # After graph execution, if a new store was created, save it to the DB session
        new_store_name = result.get("file_search_store_name")
        if new_store_name and session.file_search_store_name != new_store_name:
            session.file_search_store_name = new_store_name
            session.save(update_fields=["file_search_store_name"])

        # Save Assistant Response to DB
        ChatMessage.objects.create(
            session=session,
            role="ai",
            content=final_answer,
        )
        
        # 🔥 Auto-title logic (only once)
        if session.title == "New chat":
            session.title = message_content[:60]  # safe truncation
            session.save(update_fields=["title"])

        # Background Task
        # # Check Persona Trigger
        # check_and_trigger_persona_update(
        #     session=session, 
        #     user=request.user
        # )
        
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.chat_message_count += 1
        profile.save(update_fields=["chat_message_count"])

        if profile.chat_message_count % 4 == 0:
            ChatProfilerTriggerService.check_and_trigger(request.user)

        return Response({"answer": final_answer})
