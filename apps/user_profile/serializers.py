from rest_framework import serializers
from apps.user_profile.tasks import run_skill_gap_analysis_task
from .models import LearningInsight, SkillGap, UserProfile, Education, Experience, Project, Certification


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'institution', 'degree', 'subject_discipline', 'start_year', 'end_year', 'description']

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['id', 'organization', 'role', 'start_date', 'end_date', 'highlights']

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'tech_stack', 'description']

class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = ['id', 'name', 'issuing_organization', 'issue_date', 'credential_url']

class SkillGapSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillGap
        fields = ['id', 'gap_skill', 'reason', 'confidence', 'is_manual']
        read_only_fields = ['is_manual']
        

class LearningInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningInsight
        fields = ['id', 'insight_type', 'content', 'reason', 'is_manual']
        read_only_fields = ['is_manual', 'reason']
                
# Main serializer for UserProfile with nested serializers for related models
class UserProfileSerializer(serializers.ModelSerializer):
    # Nested fields for a complete profile view
    education_history = EducationSerializer(many=True, read_only=True)
    experience_history = ExperienceSerializer(many=True, read_only=True)
    project_history = ProjectSerializer(many=True, read_only=True)
    certification_history = CertificationSerializer(many=True, read_only=True)
    skill_gaps = SkillGapSerializer(many=True, read_only=True)
    learning_insights = LearningInsightSerializer(many=True, read_only=True)
    # Formatting resume_file URL
    resume_file_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'full_name', 'profession', 'possible_next_roles', 'phone', 'address', 
            'linkedin_url', 'resume_file', 'resume_file_url', 'summary', 
            'skills', 'total_experience_years', 'education_history', 
            'experience_history', 'project_history', 'certification_history', 'skill_gaps', 'learning_insights', 'chat_message_count'
        ]
        read_only_fields = ['user', 'total_experience_years', 'linkedin_url', 'resume_file_url']

    def get_resume_file_url(self, obj):
        if obj.resume_file:
            return obj.resume_file.url
        return None
    
 