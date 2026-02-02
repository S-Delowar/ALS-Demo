from django.contrib import admin
from django.utils.html import format_html

from .models import Article, Course, Video, Book


class BaseContentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "topic",
        "platform",
        "thumbnail_preview",
        "url_link",
        "user",
        "created_at",
    )

    list_filter = ("platform", "topic", "created_at")
    search_fields = ("title", "topic", "platform", "url")
    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
        "url",
        "thumbnail_preview",
    )

    autocomplete_fields = ("user",)
    date_hierarchy = "created_at"

    # ---------- Custom display methods ----------

    def url_link(self, obj):
        if obj.url:
            return format_html(
                '<a href="{}" target="_blank">Open</a>',
                obj.url
            )
        return "-"

    url_link.short_description = "URL"

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="height:60px; border-radius:6px;" />',
                obj.thumbnail
            )
        return "-"

    thumbnail_preview.short_description = "Thumbnail"


@admin.register(Article)
class ArticleAdmin(BaseContentAdmin):
    list_display = BaseContentAdmin.list_display + ("author",)


@admin.register(Course)
class CourseAdmin(BaseContentAdmin):
    list_display = BaseContentAdmin.list_display + ("instructor", "price")


@admin.register(Video)
class VideoAdmin(BaseContentAdmin):
    pass


@admin.register(Book)
class BookAdmin(BaseContentAdmin):
    list_display = BaseContentAdmin.list_display + ("author", "publisher")
