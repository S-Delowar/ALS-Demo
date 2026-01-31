from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserPersona


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_persona(sender, instance, created, **kwargs):
    if created:
        UserPersona.objects.create(user=instance)
