from rest_framework.routers import DefaultRouter
from django.urls import path

from apps.recommendations.views import  ArticleViewSet, CourseViewSet, VideoViewSet, BookViewSet, GenerateRecommendationsView, ArticleRecommendationAPIView, VideoRecommendationAPIView, CourseRecommendationAPIView, BookRecommendationAPIView

router = DefaultRouter()
router.register(r'articles', ArticleViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'videos', VideoViewSet)
router.register(r'books', BookViewSet)


urlpatterns = router.urls

urlpatterns += [
    path('generate/', GenerateRecommendationsView.as_view(), name='generate-recommendations'),
    path('api/recommendations/recommend-articles/', ArticleRecommendationAPIView.as_view(), name='recommend-articles'),
    path('api/recommendations/recommend-videos/', VideoRecommendationAPIView.as_view(), name='recommend-videos'),
    path('api/recommendations/recommend-courses/', CourseRecommendationAPIView.as_view(), name='recommend-courses'),
    path('api/recommendations/recommend-books/', BookRecommendationAPIView.as_view(), name='recommend-books'),
]