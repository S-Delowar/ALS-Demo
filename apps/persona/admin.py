from django.contrib import admin
from .models import UserPersona


@admin.register(UserPersona)
class UserPersonaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "get_email",      # Custom method to show email
        "full_name",      # Added full_name
        "profession",
        "level",
        "created_at",
    )

    search_fields = (
        "full_name",      # Added searching by name
        "user__email",
        "profession",
        "level",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("User Information", {
            "fields": ("user", "full_name"), # Grouped name with user
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

    # Helper method to display user email in the list view
    @admin.display(ordering='user__email', description='Email')
    def get_email(self, obj):
        return obj.user.email