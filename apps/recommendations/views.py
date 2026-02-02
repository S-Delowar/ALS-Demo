from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
import threading
from rest_framework.views import APIView

from apps.chat.models.message import ChatMessage
from apps.recommendations.services.pipeline import run_recommendation_pipeline

from .models import Article, Course, Video, Book
from .serializers import ArticleSerializer, CourseSerializer, VideoSerializer, BookSerializer


User = get_user_model()

class ReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Base viewset that ensures users can only List and Retrieve 
    their OWN content.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Override the default queryset to filter by the current user.
        """
        # 1. Get the base queryset defined in the subclass 
        # (e.g., Article.objects.all())
        queryset = super().get_queryset()
        
        # 2. Filter it so the user only sees records where user=request.user
        return queryset.filter(user=self.request.user)

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
# class GenerateRecommendationsView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         """
#         Triggers the recommendation engine.
#         Body parameters (optional if data exists in DB):
#         - profession: "Backend Developer" (overrides profile)
#         - chat_history: ["how to fix cors?", "django middleware"] (overrides DB history)
#         """
#         user = request.user
        
#         profession = user.profession
        
#         chat_history = """- What is AWS SageMaker? How to deploy models on AWS?
#                         - DO I need to learn Python for ML?"""

#         try:
#             summary = run_recommendation_pipeline(user, profession, chat_history)
#             return Response(
#                 {
#                     "message": "Recommendations generated successfully.",
#                     "summary": summary
#                 },
#                 status=status.HTTP_200_OK
#             )
#         except Exception as e:
#             return Response(
#                 {"error": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


class GenerateRecommendationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Triggers the recommendation engine.
        Gathers User queries, Persona context, and Global Activities.
        """
        user = request.user
        profession = getattr(user, 'profession', 'General Learner')

        # 1. Fetch User's Chat History (SQL)
        # Filter for messages strictly from the user (not AI)
        # Taking the last 10 to ensure context window isn't overloaded
        recent_messages = ChatMessage.objects.filter(
            session__user=user,  # <--- Spans relationship: Message -> Session -> User
            role='user'
        ).order_by('-created_at')[:10]

        # Convert queryset to a single string for the pipeline
        if recent_messages:
            # Reverse to maintain chronological order in the prompt
            chat_history_text = "\n".join(
                [f"- {msg.content}" for msg in reversed(recent_messages)]
            )
        else:
            chat_history_text = "No recent specific questions asked."

        try:
            # 2. Pass data to the orchestrator
            summary = run_recommendation_pipeline(user, profession, chat_history_text)
            
            return Response(
                {
                    "message": "Recommendations generated successfully.",
                    "summary": summary
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            # Log the error here in production
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )