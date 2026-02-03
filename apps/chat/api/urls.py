from django.urls import path
from .views import (
    ChatbotAPIView,
    CreateChatSessionView,
    ChatSessionDetailView,
    SendMessageView,
    ChatHistoryView,
)

urlpatterns = [
    path("sessions/", CreateChatSessionView.as_view()),
    path("sessions/<int:session_id>/", ChatSessionDetailView.as_view()),
    path("sessions/<int:session_id>/message/send/", ChatbotAPIView.as_view()),
    path("sessions/<int:session_id>/history/", ChatHistoryView.as_view()),
]
