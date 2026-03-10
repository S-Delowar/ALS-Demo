from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.db import transaction

from apps.recommendations.tasks import generate_user_recommendations_task
from apps.user_profile.models import UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def handle_new_user_creation(sender, instance, created, **kwargs):
    """
    Automatically creates a UserProfile and triggers recommendation generation when a new User is registered.
    """
    if created:
        UserProfile.objects.create(
            user=instance,
            full_name=instance.full_name or "",
            profession=instance.profession or ""
        )
        
        transaction.on_commit(
            lambda: generate_user_recommendations_task.delay(user_id=instance.id)
            )
        
        
