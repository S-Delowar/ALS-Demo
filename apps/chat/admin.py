from django.contrib import admin
from .models.session import ChatSession
from .models.message import ChatMessage


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ("role", "content", "metadata", "created_at")
    can_delete = False
    show_change_link = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "user__email", "user__username")
    readonly_fields = ("created_at", "updated_at")

    inlines = [ChatMessageInline]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "role", "short_content", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("content",)
    readonly_fields = ("created_at",)

    def short_content(self, obj):
        return obj.content[:60]

    short_content.short_description = "Content"
