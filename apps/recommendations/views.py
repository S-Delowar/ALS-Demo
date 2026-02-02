from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
import threading
from rest_framework.views import APIView

from apps.recommendations.services.pipeline import run_recommendation_pipeline

from .models import Article, Course, Video, Book
from .serializers import ArticleSerializer, CourseSerializer, VideoSerializer, BookSerializer


User = get_user_model()


class ReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Base viewset to ensure users can only List and Retrieve.
    Authentication is required.
    """
    permission_classes = [permissions.IsAuthenticated]

class ArticleViewSet(ReadOnlyViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

class CourseViewSet(ReadOnlyViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class VideoViewSet(ReadOnlyViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

class BookViewSet(ReadOnlyViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    
# ================================
# Generate Recommendations View
# ================================
class GenerateRecommendationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Triggers the recommendation engine.
        Body parameters (optional if data exists in DB):
        - profession: "Backend Developer" (overrides profile)
        - chat_history: ["how to fix cors?", "django middleware"] (overrides DB history)
        """
        user = request.user
        
        profession = user.profession
        
        chat_history = """- What is AWS SageMaker? How to deploy models on AWS?
                        - DO I need to learn Python for ML?"""

        try:
            summary = run_recommendation_pipeline(user, profession, chat_history)
            return Response(
                {
                    "message": "Recommendations generated successfully.",
                    "summary": summary
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )