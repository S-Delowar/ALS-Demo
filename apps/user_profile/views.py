
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db import transaction

from .models import LearningInsight, SkillGap, UserProfile, Education, Experience, Project, Certification
from .serializers import (
    LearningInsightSerializer, SkillGapSerializer, UserProfileSerializer, EducationSerializer, 
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
    trigger_skill_gap = True

    def perform_create(self, serializer):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        serializer.save(profile=profile)
        if self.trigger_skill_gap:
            trigger_skill_gap_agent(self.request.user.id)
        
    def perform_update(self, serializer):
        super().perform_update(serializer)
        if self.trigger_skill_gap:
            trigger_skill_gap_agent(self.request.user.id) # Trigger on edit

    def perform_destroy(self, instance):
        user_id = self.request.user.id
        instance.delete()
        if self.trigger_skill_gap:
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
class SkillGapViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin, 
                      mixins.UpdateModelMixin, 
                      mixins.DestroyModelMixin, 
                      viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SkillGapSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        return SkillGap.objects.filter(profile__user=self.request.user)

    def perform_create(self, serializer):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        # If the user creates it manually, we lock it so AI doesn't delete it
        serializer.save(profile=profile, is_manual=True) 

    def perform_update(self, serializer):
        # If they edit an AI-generated one, it becomes "theirs"
        serializer.save(is_manual=True)
        

# --- Learning Insight ViewSet for AI-generated insights ---
class LearningInsightViewSet(NestedEntityViewSet):
    serializer_class = LearningInsightSerializer
    
    # Turn off the skill gap agent for this specific endpoint
    trigger_skill_gap = False 

    def get_queryset(self):
        return LearningInsight.objects.filter(profile__user=self.request.user)

    def perform_create(self, serializer):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        # Force is_manual=True so the Chat Profiler AI respects the user's manual entry
        serializer.save(profile=profile, is_manual=True)
        
    def perform_update(self, serializer):
        # If the user edits an AI-generated insight, claim it as manual
        serializer.save(is_manual=True)
        
        
        

# Trigger Skill Gap Analyzer Agent
class TriggerSkillGapAnalysisView(APIView):
    """
    Dedicated endpoint to manually trigger the AI Skill Gap Analysis task.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        user_id = request.user.id
        
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)
        
        transaction.on_commit(lambda: run_skill_gap_analysis_task.delay(user_id))
    
        return Response(
            {
                "status": "Accepted",
                "message": "Skill gap analysis has been queued and is running in the background. You will see updated skill gaps shortly."
            },
            status=status.HTTP_202_ACCEPTED
        )