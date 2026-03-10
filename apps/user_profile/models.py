from django.db import models
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True)
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
    chat_message_count = models.IntegerField(
        default=0, 
        help_text="Tracks total user messages to trigger background profiler"
    )

    def __str__(self):
        return self.full_name or self.user.username
    
    def save(self, *args, **kwargs):
        # 1. Save the UserProfile to the database first
        super().save(*args, **kwargs)

        # 2. Sync the updated name and profession back to the User model.
        # We use .update() here because it fires a direct SQL UPDATE query.
        # If we used self.user.save(), it would trigger the post_save signal 
        # again and cause an infinite loop.
        User = self.user.__class__
        User.objects.filter(id=self.user.id).update(
            full_name=self.full_name,
            profession=self.profession
        )


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
    
    
# Model to capture user goals, preferences, and focus areas for personalized learning recommendations
class LearningInsight(models.Model):
    INSIGHT_TYPES = (
        ('goal', 'Goal'),
        ('preference', 'Preference'),
        ('focus_area', 'Focus Area'),
    )
    
    profile = models.ForeignKey(UserProfile, related_name='learning_insights', on_delete=models.CASCADE)
    insight_type = models.CharField(max_length=20, choices=INSIGHT_TYPES)
    # Kept short for mobile UI compatibility
    content = models.CharField(max_length=300, help_text="Short text describing the user's goal, preference, or focus area")
    reason = models.CharField(
        max_length=500, 
        null=True, 
        blank=True, 
        help_text="AI justification for this insight based on the user's chat history."
    )
    # Protects user edits from the background Celery task
    is_manual = models.BooleanField(
        default=False, 
        help_text="True if the user added/edited this manually. Protects from AI overwrites."
    )

    class Meta:
        # Prevents the exact same goal from appearing twice for the same user
        unique_together = ('profile', 'insight_type', 'content')

    def __str__(self):
        return f"{self.get_insight_type_display()}: {self.content} ({self.profile.full_name})"