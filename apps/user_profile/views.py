
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import SkillGap, UserProfile, Education, Experience, Project, Certification
from .serializers import (
    SkillGapSerializer, UserProfileSerializer, EducationSerializer, 
    ExperienceSerializer, ProjectSerializer, CertificationSerializer
)
from .tasks import process_resume_task, run_skill_gap_analysis_task



# --- Helper Function ---
def trigger_skill_gap_agent(user_id):
    """Fires the background task. Add a small delay if needed to ensure DB commits."""
    run_skill_gap_analysis_task.delay(user_id)
    

# --- Main Profile ViewSet ---
# Inherits ONLY UpdateModelMixin (for PATCH) and GenericViewSet (for custom actions)
class ProfileViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    http_method_names = ['get', 'post', 'patch']  # Explicitly blocks PUT and DELETE

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='upload-resume')
    def upload_resume(self, request):
        file = request.FILES.get('resume_file')
        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.resume_file = file
        profile.save()

        process_resume_task.delay(request.user.id, profile.resume_file.path)
        return Response({"status": "Processing"}, status=status.HTTP_202_ACCEPTED)
    
    
    def perform_update(self, serializer):
        """Triggers when user updates their main profile (skills, next roles, etc)"""
        super().perform_update(serializer)
        trigger_skill_gap_agent(self.request.user.id)


# --- Nested Entity ViewSets ---
# We create a custom base class so we don't repeat code for all 4 nested models
class NestedEntityViewSet(mixins.CreateModelMixin, 
                          mixins.UpdateModelMixin, 
                          mixins.DestroyModelMixin, 
                          viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'patch', 'delete'] # Explicitly blocks GET and PUT

    def perform_create(self, serializer):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        serializer.save(profile=profile)
        trigger_skill_gap_agent(self.request.user.id)
        
    def perform_update(self, serializer):
        super().perform_update(serializer)
        trigger_skill_gap_agent(self.request.user.id) # Trigger on edit

    def perform_destroy(self, instance):
        user_id = self.request.user.id
        instance.delete()
        trigger_skill_gap_agent(user_id)


# Now we just inherit the custom base class for a beautifully clean file
class EducationViewSet(NestedEntityViewSet):
    serializer_class = EducationSerializer
    def get_queryset(self):
        return Education.objects.filter(profile__user=self.request.user)

class ExperienceViewSet(NestedEntityViewSet):
    serializer_class = ExperienceSerializer
    def get_queryset(self):
        return Experience.objects.filter(profile__user=self.request.user)

class ProjectViewSet(NestedEntityViewSet):
    serializer_class = ProjectSerializer
    def get_queryset(self):
        return Project.objects.filter(profile__user=self.request.user)

class CertificationViewSet(NestedEntityViewSet):
    serializer_class = CertificationSerializer
    def get_queryset(self):
        return Certification.objects.filter(profile__user=self.request.user)
    
    
# --- Skill Gap ViewSet for User Edits ---
class SkillGapViewSet(mixins.CreateModelMixin, 
                      mixins.UpdateModelMixin, 
                      mixins.DestroyModelMixin, 
                      viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SkillGapSerializer
    http_method_names = ['post', 'patch', 'delete']

    def get_queryset(self):
        return SkillGap.objects.filter(profile__user=self.request.user)

    def perform_create(self, serializer):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        # If the user creates it manually, we lock it so AI doesn't delete it
        serializer.save(profile=profile, is_manual=True) 

    def perform_update(self, serializer):
        # If they edit an AI-generated one, it becomes "theirs"
        serializer.save(is_manual=True)