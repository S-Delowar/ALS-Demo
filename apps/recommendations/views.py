from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
import threading
from rest_framework.views import APIView

from apps.chat.models.message import ChatMessage
from apps.recommendations.services.context import get_topics_plan
from apps.recommendations.services.pipeline import run_recommendation_pipeline
from apps.recommendations.services.pipeline_02 import recommend_articles, recommend_books, recommend_courses, recommend_videos, run_full_pipeline
from apps.recommendations.tasks import generate_recommendation_for_user

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



# class GenerateRecommendationsView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request):
#         # Trigger the celery task asynchronously immediately
#         generate_recommendation_for_user.delay(request.user.id)
        
#         return Response(
#             {"message": "We are generating your recommendations in the background. Please check back in a few moments."},
#             status=status.HTTP_202_ACCEPTED
#         )
        
 
 

# class FullPipelineAPIView(APIView):
#     def post(self, request):
#         profession = request.data.get('profession', '')
#         chat_history = request.data.get('chat_history', '')
        
#         summary = run_full_pipeline(request.user, profession, chat_history)
#         return Response(summary, status=status.HTTP_201_CREATED)

       
        
class BaseRecommendationView(APIView):
    """Base class to handle context extraction for specific endpoints."""
    
    def get_topics(self, request):
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
            
        # Call the LLM to get the plan
        return get_topics_plan(request.user, profession, chat_history_text)



class ArticleRecommendationAPIView(BaseRecommendationView):
    def post(self, request):
        topics_plan = self.get_topics(request)
        
        try:
            # 2. Pass data to the orchestrator
            summary = recommend_articles(request.user, topics_plan)
            
            print(f"Article recommendation summary: {summary}")
            
            return Response(
                {
                    "message": "Recommended articles generated successfully.",
                    "summary": summary
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            # Log the error here in production
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            

class VideoRecommendationAPIView(BaseRecommendationView):
    def post(self, request):
        topics_plan = self.get_topics(request)
        try:
            # 2. Pass data to the orchestrator
            summary = recommend_videos(request.user, topics_plan)
            
            print(f"Video recommendation summary: {summary}")
            
            return Response(
                {
                    "message": "Recommended videos generated successfully.",
                    "summary": summary
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            # Log the error here in production
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseRecommendationAPIView(BaseRecommendationView):
    def post(self, request):
        topics_plan = self.get_topics(request)
        try:
            # 2. Pass data to the orchestrator
            summary = recommend_courses(request.user, topics_plan)
            
            print(f"Course recommendation summary: {summary}")
            
            return Response(
                {
                    "message": "Recommended courses generated successfully.",
                    "summary": summary
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            # Log the error here in production
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BookRecommendationAPIView(BaseRecommendationView):
    def post(self, request):
        topics_plan = self.get_topics(request)
        try:
            summary = recommend_books(request.user, topics_plan)
            
            print(f"Book recommendation summary: {summary}")
            
            return Response(
                {
                    "message": "Recommended books generated successfully.",
                    "summary": summary
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            # Log the error here in production
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
