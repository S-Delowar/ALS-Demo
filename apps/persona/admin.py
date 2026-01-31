from django.contrib import admin
from .models import UserPersona


@admin.register(UserPersona)
class UserPersonaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "profession",
        "level",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "profession",
        "level",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("User", {
            "fields": ("user",),
        }),
        ("Persona Details", {
            "fields": ("profession", "level"),
        }),
        ("Preferences", {
            "fields": ("preferences",),
        }),
        ("Meta", {
            "fields": ("created_at", "updated_at"),
        }),
    )
