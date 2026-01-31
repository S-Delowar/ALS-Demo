from django.urls import path
from .views import (
    SearchDocumentsView,
    UploadDocumentView,
)

urlpatterns = [
    path("upload/", UploadDocumentView.as_view()),
    path("search/", SearchDocumentsView.as_view()),
]
