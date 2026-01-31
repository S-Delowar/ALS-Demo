from django.db import models
from django.conf import settings
from apps.chat.models.session import ChatSession


class UserDocument(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    filename = models.CharField(max_length=500)
    file = models.FileField(upload_to="uploads/documents/")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename
