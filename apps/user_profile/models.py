from django.db import models
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=255, blank=True)
    profession = models.CharField(max_length=255, blank=True)
    possible_next_roles = models.JSONField(default=list, blank=True)
    total_experience_years = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        default=0.0,
        help_text="Calculated from first job start date to present"
    )
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    linkedin_url = models.URLField(blank=True)
    resume_file = models.FileField(upload_to='resumes/%Y/%m/', null=True, blank=True)
    summary = models.TextField(blank=True)
    skills = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.name or self.user.username


class Education(models.Model):
    profile = models.ForeignKey(UserProfile, related_name='education_history', on_delete=models.CASCADE)
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    subject_discipline = models.CharField(max_length=255, blank=True)
    start_year = models.CharField(max_length=10)
    end_year = models.CharField(max_length=10, blank=True, null=True)
    description = models.TextField(blank=True)


class Experience(models.Model):
    profile = models.ForeignKey(UserProfile, related_name='experience_history', on_delete=models.CASCADE)
    organization = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    start_date = models.CharField(max_length=50)
    end_date = models.CharField(max_length=50, blank=True, null=True)
    highlights = models.JSONField(default=list)


class Project(models.Model):
    profile = models.ForeignKey(UserProfile, related_name='project_history', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    tech_stack = models.JSONField(default=list)
    description = models.TextField()
    
    
class Certification(models.Model):
    profile = models.ForeignKey(UserProfile, related_name='certification_history', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255)
    issue_date = models.CharField(max_length=50, blank=True)
    credential_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.issuing_organization}"
    
    
class SkillGap(models.Model):
    profile = models.ForeignKey(UserProfile, related_name='skill_gaps', on_delete=models.CASCADE)
    gap_skill = models.CharField(max_length=255)
    reason = models.TextField(help_text="Short explanation for justification of this gap", null=True, blank=True)
    confidence = models.FloatField(
        default=0.5, 
        help_text="Confidence level from 0.0 to 1.0"
    )
    is_manual = models.BooleanField(
        default=False, 
        help_text="True if the user added/edited this manually. Protects from AI overwrites."
    )

    def __str__(self):
        return f"{self.skill_gap} ({self.profile.name})"