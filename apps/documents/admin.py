from django.contrib import admin
from .models import UserDocument


@admin.register(UserDocument)
class UserDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "filename", "user", "session", "created_at")
    list_filter = ("created_at",)
    search_fields = ("filename", "user__email", "user__username")
    readonly_fields = ("created_at",)

    raw_id_fields = ("user", "session")
