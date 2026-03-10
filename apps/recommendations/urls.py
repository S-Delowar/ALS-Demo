from rest_framework.routers import DefaultRouter
from django.urls import path

from apps.recommendations.views import  ArticleViewSet, CourseViewSet, SavedRecommendationsView, ToggleSaveItemView, VideoViewSet, BookViewSet, GenerateRecommendationsAllView, GenerateArticleRecommendationAPIView, GenerateVideoRecommendationAPIView, GenerateCourseRecommendationAPIView, GenerateBookRecommendationAPIView

router = DefaultRouter()
router.register(r'articles', ArticleViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'videos', VideoViewSet)
router.register(r'books', BookViewSet)


urlpatterns = router.urls

urlpatterns += [
    path('generate-all/', GenerateRecommendationsAllView.as_view(), name='generate-recommendations'),
    path('generate-articles/', GenerateArticleRecommendationAPIView.as_view(), name='recommend-articles'),
    path('generate-videos/', GenerateVideoRecommendationAPIView.as_view(), name='recommend-videos'),
    path('generate-courses/', GenerateCourseRecommendationAPIView.as_view(), name='recommend-courses'),
    path('generate-books/', GenerateBookRecommendationAPIView.as_view(), name='recommend-books'),
    
    path('toggle-save/', ToggleSaveItemView.as_view(), name='toggle-save'),
    path('saved/', SavedRecommendationsView.as_view(), name='saved-recommendations'),
]