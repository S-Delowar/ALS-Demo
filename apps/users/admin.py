from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = (
        "email",
        "profession",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "profession")
    search_fields = ("email", "profession")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("profession",)}),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "profession", "password1", "password2"),
            },
        ),
    )

    readonly_fields = ("last_login",)

    filter_horizontal = ("groups", "user_permissions")
