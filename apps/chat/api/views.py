from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


from apps.chat.models import ChatSession, ChatMessage
from apps.persona.services import check_and_trigger_persona_update
from .serializers import ChatSessionSerializer, ChatMessageSerializer


class CreateChatSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session = ChatSession.objects.create(
            user=request.user,
        )
        return Response(ChatSessionSerializer(session).data)


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

    def post(self, request, session_id):
        # 1. Retrieve the session securely
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        message_content = request.data.get("message")

        if not message_content:
            return Response({"error": "Message content is required"}, status=400)

        # 2. Save User Message to DB
        ChatMessage.objects.create(
            session=session,
            role="user",
            content=message_content,
        )

        # 3. Fetch History (Includes the message just created)
        # We fetch the last 10 messages to keep context window efficient
        history_queryset = session.messages.order_by("-created_at")[:10]
        history = list(history_queryset.values("role", "content"))[::-1]  #Reverse - oldest first

        # 4. Prepare State for LangGraph/StateGraph
        state = {
            "user_id": request.user.id,
            "session_id": session.id,
            "message": message_content,
            "history": history,
            "intent": "",       # specific keys required by your ChatState
            "final_answer": None
        }

        # 5. Invoke the Graph
        result = chatbot_graph.invoke(state)
        final_answer = result.get("final_answer", "No response generated.")

        # 6. Save Assistant Response to DB
        ChatMessage.objects.create(
            session=session,
            role="ai",
            content=final_answer,
        )

        return Response({"answer": final_answer})
