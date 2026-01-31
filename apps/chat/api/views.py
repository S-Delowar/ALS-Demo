from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


from apps.chat.models import ChatSession, ChatMessage
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
