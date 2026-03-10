from django.contrib import admin
from .models import LearningInsight, SkillGap, UserProfile, Education, Experience, Project, Certification

# --- Inlines for a nested UI ---

class EducationInline(admin.TabularInline):
    model = Education
    extra = 0  # Prevents empty extra rows from cluttering the UI

class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0

class ProjectInline(admin.StackedInline): # Stacked is better for long descriptions
    model = Project
    extra = 0

class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 0

# --- Main Profile Admin ---

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # What you see in the main list view
    list_display = ('full_name', 'profession', 'user', 'total_experience_years', 'phone')
    search_fields = ('full_name', 'profession', 'skills', 'user__email', 'user__username')
    list_filter = ('profession', 'total_experience_years')
    
    # Read-only fields to prevent accidental tampering with AI-calculated data
    readonly_fields = ('total_experience_years',)
    
    # Organizing the detail view with fieldsets
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'full_name', 'profession', 'summary', 'total_experience_years')
        }),
        ('Contact & Links', {
            'fields': ('phone', 'address', 'linkedin_url', 'resume_file')
        }),
        ('Technical Profile', {
            'fields': ('skills',)
        }),
    )

    # Adding the inlines so everything is editable in one place
    inlines = [
        EducationInline, 
        ExperienceInline, 
        ProjectInline, 
        CertificationInline
    ]

# Optionally register the others individually if you need separate access
admin.site.register(Education)
admin.site.register(Experience)
admin.site.register(Project)
admin.site.register(Certification)
admin.site.register(SkillGap)
admin.site.register(LearningInsight)