from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import ChatSession
from .tasks import delete_gemini_file_store

@receiver(post_delete, sender=ChatSession)
def cleanup_gemini_store(sender, instance, **kwargs):
    """Triggers the Celery task when a ChatSession is deleted."""
    if instance.file_search_store_name:
        delete_gemini_file_store.delay(instance.file_search_store_name)