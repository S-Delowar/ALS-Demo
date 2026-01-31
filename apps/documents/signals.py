from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import UserDocument


@receiver(post_delete, sender=UserDocument)
def delete_document_file(sender, instance, **kwargs):
    """
    Delete file from storage when UserDocument is deleted.
    """
    if instance.file:
        instance.file.delete(save=False)
