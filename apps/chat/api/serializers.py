from rest_framework import serializers
from apps.chat.models import ChatSession, ChatMessage


class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ["id", "title", "created_at", "updated_at"]


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "role", "content", "metadata", "created_at"]
