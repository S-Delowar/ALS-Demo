from annotated_types import T
from django.db import models
from .session import ChatSession


class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ("user", "User"),
        ("ai", "Ai"),
    )

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()

    # for intent, tools_used, etc (later)
    metadata = models.JSONField(default=dict, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role} @ {self.created_at}"
