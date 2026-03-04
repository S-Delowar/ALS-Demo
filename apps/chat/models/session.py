from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sessions"
    )

    title = models.CharField(max_length=255, default="New chat")
    is_active = models.BooleanField(default=True)

    # Stores the Gemini RAG store ID (e.g., 'fileSearchStores/my-store-123')
    file_search_store_name = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Google Gemini File Search Store ID for this session"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session({self.id}) - {self.title}"