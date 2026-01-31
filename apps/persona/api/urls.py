from django.urls import path
from .views import MyPersonaView

urlpatterns = [
    path("me/", MyPersonaView.as_view(), name="my-persona"),
]
