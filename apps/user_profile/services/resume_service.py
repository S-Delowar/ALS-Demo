import pymupdf  # PyMuPDF
import json
import logging
from django.conf import settings
from datetime import datetime
from dateutil.relativedelta import relativedelta
from google import genai
from ..models import Certification, UserProfile, Education, Experience, Project

logger = logging.getLogger(__name__)


client = genai.Client()


def generate_resume_parsing_prompt(resume_text):
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    return f"""
    Act as a Senior Technical Recruiter and Data Extraction Specialist. 
    Your task is to parse the provided RESUME TEXT into a precise JSON object matching the schema below.

    ### STRICT RULES:
    1. **Dates**: Normalize ALL dates to 'YYYY-MM-DD'. 
       - If only a year is provided (e.g., "2022"), use "2022-01-01".
       - If "Present" or "Current" is mentioned, use today's date: {current_date}.s
    2. **Missing Data**: If a field or section is missing, return an empty string "" for strings or an empty list [] for collections. Do not invent data.
    3. **Possible Next Roles**: think about the candidate's current profession and skills, and suggest 2-3 logical next career roles they might be targeting. This should be based on common career progression paths in the industry.
    4. **Experience Calculation**: Based on the 'start_date' of the earliest professional role and today's date ({current_date}), calculate the total years of experience as a decimal (e.g., 3.5).
    5. **Formatting**: Return ONLY the JSON object. No markdown headers, no conversational filler.

    ### TARGET JSON SCHEMA:
    {{
        "name": "Full Name",
        "profession": "Current job title or headline",
        "possible_next_roles": ["Role 1", "Role 2"],
        "phone": "Contact number",
        "address": "Location or full address",
        "linkedin_url": "URL",
        "summary": "Professional summary or bio",
        "skills": ["Skill 1", "Skill 2"],
        "total_experience_years": 0.0,
        "education": [
            {{
                "institution": "University Name",
                "degree": "e.g. B.Sc.",
                "subject_discipline": "Field of study",
                "start_year": "YYYY-MM-DD",
                "end_year": "YYYY-MM-DD",
                "description": ""
            }}
        ],
        "experience": [
            {{
                "organization": "Company Name",
                "role": "Job Title",
                "start_date": "YYYY-MM-DD",
                "end_date": "YYYY-MM-DD",
                "highlights": ["Achievement 1", "Achievement 2"]
            }}
        ],
        "projects": [
            {{
                "title": "Project Name",
                "tech_stack": ["Tech 1", "Tech 2"],
                "description": "Short summary"
            }}
        ],
        "certifications": [
            {{
                "name": "Cert Name",
                "issuing_organization": "Issuer",
                "issue_date": "YYYY-MM-DD",
                "credential_url": "URL"
            }}
        ]
    }}

    ### RESUME TEXT TO PARSE:
    {resume_text}
    """



class ResumeService:
    @staticmethod
    def extract_text_from_pdf(file_path):
        text = ""
        try:
            with pymupdf.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
            logger.info(f"======*******\nSuccessfully extracted text from Resume PDF: {file_path}\n\n==========************")
            logger.info(f"===========********************=====================\nExtracted Text: {text}\n\n================*************=====================")
            return text
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            return ""

    @staticmethod
    def call_gemini_parser(resume_text):        
        prompt = generate_resume_parsing_prompt(resume_text)
        response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config={
            "response_mime_type": "application/json",
        },
    )
        # Handle markdown blocks if Gemini returns them
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    
    @staticmethod
    def calculate_experience(experience_list):
        """
        Calculates total years from the earliest start date to now.
        """
        if not experience_list:
            return 0.0

        earliest_date = datetime.now()
        
        for exp in experience_list:
            start_str = exp.get('start_date', '')
            try:
                # Attempt to parse common resume formats
                # Gemini usually returns normalized 'YYYY-MM-DD' if asked
                dt = datetime.strptime(start_str, '%Y-%m-%d')
                if dt < earliest_date:
                    earliest_date = dt
            except (ValueError, TypeError):
                continue

        delta = relativedelta(datetime.now(), earliest_date)
        # Return as decimal (e.g., 3.5 years)
        total_years = delta.years + (delta.months / 12.0)
        return round(total_years, 1)

    @classmethod
    def update_profile_from_json(cls, user_id, data):
        profile = UserProfile.objects.get(user_id=user_id)
        # Calculate experience before saving
        exp_list = data.get('experience', [])
        experience_years = cls.calculate_experience(exp_list)
        
        # Update Profile
        profile.name = data.get('name', '')
        profile.profession = data.get('profession', '')
        profile.possible_next_roles = data.get('possible_next_roles', [])
        profile.phone = data.get('phone', '')
        profile.total_experience_years = experience_years
        profile.address = data.get('address', '')
        profile.linkedin_url = data.get('linkedin_url', '')
        profile.summary = data.get('summary', '')
        profile.skills = data.get('skills', [])
        profile.save()

        # Update Related Data (Atomic Refresh)
        profile.education_history.all().delete()
        for edu in data.get('education', []):
            Education.objects.create(profile=profile, **edu)

        profile.experience_history.all().delete()
        for exp in data.get('experience', []):
            Experience.objects.create(profile=profile, **exp)

        profile.project_history.all().delete()
        for proj in data.get('projects', []):
            Project.objects.create(profile=profile, **proj)
            
        profile.certification_history.all().delete()
        for cert in data.get('certifications', []):
            Certification.objects.create(profile=profile, **cert)