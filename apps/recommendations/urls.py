from rest_framework.routers import DefaultRouter
from django.urls import path

from apps.recommendations.views import  ArticleViewSet, CourseViewSet, VideoViewSet, BookViewSet, GenerateRecommendationsView

router = DefaultRouter()
router.register(r'articles', ArticleViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'videos', VideoViewSet)
router.register(r'books', BookViewSet)


urlpatterns = router.urls

urlpatterns += [
    path('generate/', GenerateRecommendationsView.as_view(), name='generate-recommendations'),
]