from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CertificationViewSet, EducationViewSet, ExperienceViewSet, LearningInsightViewSet, ProfileViewSet, ProjectViewSet, SkillGapViewSet, TriggerSkillGapAnalysisView

# Using a router is standard for ViewSets
router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='user-profile')

# Dedicated micro-update routes
router.register(r'educations', EducationViewSet, basename='education')
router.register(r'experiences', ExperienceViewSet, basename='experience')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'certifications', CertificationViewSet, basename='certification')
router.register(r'skill-gaps', SkillGapViewSet, basename='skill-gap')  # <-- 2. Register the endpoint
router.register(r'learning-insights', LearningInsightViewSet, basename='learning-insight')

urlpatterns = [
    path('skill-gaps/analyze/', TriggerSkillGapAnalysisView.as_view(), name='trigger-skill-gap-analysis'),  

    # This includes:
    # GET /api/profiles/me/ (via a custom action or filtering)
    # POST /api/profiles/upload_resume/
    # GET /api/profiles/{id}/
    # PATCH /api/profiles/{id}/
    path('', include(router.urls)),
]