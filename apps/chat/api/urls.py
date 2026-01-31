from django.urls import path
from .views import (
    CreateChatSessionView,
    SendMessageView,
    ChatHistoryView,
)

urlpatterns = [
    path("sessions/", CreateChatSessionView.as_view()),
    path("sessions/<int:session_id>/messages/", SendMessageView.as_view()),
    path("sessions/<int:session_id>/history/", ChatHistoryView.as_view()),
]
