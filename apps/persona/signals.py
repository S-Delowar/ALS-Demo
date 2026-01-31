from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from apps.persona.tasks import generate_global_activities_for_profession
from .models import UserPersona


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_persona(sender, instance, created, **kwargs):
    if created:
        UserPersona.objects.create(user=instance, profession=instance.profession)


@receiver(post_save, sender=UserPersona)
def trigger_global_activities(sender, instance, created, **kwargs):
    """
    Trigger global activity generation when profession is first set.
    """

    if instance.profession:
        generate_global_activities_for_profession.delay(
            instance.profession
        )