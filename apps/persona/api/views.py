from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.persona.models import UserPersona
from .serializers import UserPersonaSerializer


class MyPersonaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        persona = UserPersona.objects.get(user=request.user)
        serializer = UserPersonaSerializer(persona)
        return Response(serializer.data)

    def patch(self, request):
    # Use get_object_or_404 to return a clean 404 instead of a 500 error
        persona = get_object_or_404(UserPersona, user=request.user)
        
        serializer = UserPersonaSerializer(
            persona, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
