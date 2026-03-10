from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, mixins
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema

from apps.chat.models.message import ChatMessage
from apps.recommendations.services.context import get_topics_plan
from apps.recommendations.services.pipeline import run_recommendation_pipeline
from apps.recommendations.services.pipeline_02 import recommend_articles, recommend_books, recommend_courses, recommend_videos
from apps.recommendations.tasks import generate_user_recommendations_task
# from apps.recommendations.tasks import generate_recommendation_for_user

from .models import Article, Course, Video, Book
from .serializers import ArticleSerializer, CourseSerializer, ToggleSaveSerializer, VideoSerializer, BookSerializer


User = get_user_model()

class ListOnlyViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Base viewset that ensures users can ONLY List their OWN content.
    Detail/Retrieve views (by ID) are disabled.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Override the default queryset to filter by the current user.
        """
        # 1. Get the base queryset defined in the subclass 
        queryset = super().get_queryset()
        
        # 2. Filter it so the user only sees records where user=request.user
        return queryset.filter(user=self.request.user)


# specific viewsets inherit from the new ListOnlyViewSet
class ArticleViewSet(ListOnlyViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

class CourseViewSet(ListOnlyViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class VideoViewSet(ListOnlyViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

class BookViewSet(ListOnlyViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    


class GenerateRecommendationsAllView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Triggers the recommendation engine asynchronously via Celery.
        """
        try:
            # 1. Dispatch the background task
            # The task handles the DB queries, LLM prompting (Gemini 2.5 Flash), and scraping
            task = generate_user_recommendations_task.delay(user_id=request.user.id)
            
            # 2. Return an immediate response to the client
            return Response(
                {
                    "message": "Recommendations are being generated in the background.",
                    "task_id": task.id  # Useful for tracking status on the frontend
                },
                # HTTP 202 Accepted is the REST standard for async processing
                status=status.HTTP_202_ACCEPTED 
            )
            
        except Exception as e:
            # Log the error in production
            return Response(
                {"error": "Failed to start the recommendation pipeline."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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



class GenerateArticleRecommendationAPIView(BaseRecommendationView):
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
            

class GenerateVideoRecommendationAPIView(BaseRecommendationView):
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


class GenerateCourseRecommendationAPIView(BaseRecommendationView):
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


class GenerateBookRecommendationAPIView(BaseRecommendationView):
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
        


# Toggle Save recommendation items
class ToggleSaveItemView(APIView):
    """
    Unified endpoint to toggle the 'is_saved' status of any recommendation item.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=ToggleSaveSerializer)
    def post(self, request):
        content_type = request.data.get('content_type')
        item_id = request.data.get('item_id')

        # Validate payload
        if not content_type or not item_id:
            return Response(
                {"error": "Both 'content_type' and 'item_id' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        #Map the string to the actual Django Model
        model_map = {
            'article': Article,
            'book': Book,
            'course': Course,
            'video': Video
        }
        ModelClass = model_map.get(content_type.lower())
        
        if not ModelClass:
            return Response(
                {"error": f"Invalid content_type. Must be one of: {list(model_map.keys())}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch the item, ensuring the current user actually owns it
        item = get_object_or_404(ModelClass, id=item_id, user=request.user)

        # Toggle the boolean using the exact field name 'is_saved'
        item.is_saved = not item.is_saved
        item.save(update_fields=['is_saved'])

        # Return the updated state
        return Response({
            "message": "Item saved status updated successfully.",
            "is_saved": item.is_saved, 
            "content_type": content_type,
            "item_id": item_id
        }, status=status.HTTP_200_OK)


# List the saved Recommendation items for the user
class SavedRecommendationsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Retrieves all saved items for the user, grouped by content type.
        """
        user = request.user

        # 1. Query the 4 separate tables
        # Using .order_by('-created_at') so the most recently saved/created show first
        articles = Article.objects.filter(user=user, is_saved=True).order_by('-created_at')
        videos = Video.objects.filter(user=user, is_saved=True).order_by('-created_at')
        courses = Course.objects.filter(user=user, is_saved=True).order_by('-created_at')
        books = Book.objects.filter(user=user, is_saved=True).order_by('-created_at')

        # 2. Serialize and group into a single dictionary
        return Response({
            "articles": ArticleSerializer(articles, many=True).data,
            "videos": VideoSerializer(videos, many=True).data,
            "courses": CourseSerializer(courses, many=True).data,
            "books": BookSerializer(books, many=True).data,
        })