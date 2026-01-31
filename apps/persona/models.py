from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings


class UserPersona(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="persona"
    )

    profession = models.CharField(max_length=255, blank=True, null=True)
    level = models.CharField(max_length=100, blank=True, null=True)

    # flexible but structured
    preferences = models.JSONField(default=dict, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Persona({self.user_id})"
