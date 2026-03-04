import json
import logging
from google import genai
from apps.user_profile.models import SkillGap, UserProfile


logger = logging.getLogger(__name__)

client = genai.Client()


class SkillGapAgentService:
    @staticmethod
    def build_profile_context(profile):
        """Serializes the user's entire profile context for the LLM."""
        return json.dumps({
            "profession": profile.profession,
            "skills": profile.skills,
            "possible_next_roles": profile.possible_next_roles,
            "experience_years": float(profile.total_experience_years),
            "education": list(profile.education_history.values('degree', 'subject_discipline')),
            "experience": list(profile.experience_history.values('role', 'organization', 'highlights')),
            "projects": list(profile.project_history.values('title', 'tech_stack')),
            "certifications": list(profile.certification_history.values('name'))
        }, default=str)

    @staticmethod
    def generate_skill_gap_prompt(profile_context):
        return f"""
        Act as an Expert AI Career Coach and Skill Gap Analyst.
        Review the following candidate profile. Look at their current profession, skills, experience, projects, and possible_next_roles.
        
        Compare their current profile against global industry standards and requirements for those next roles.
        Identify the missing skills, tools, or knowledge areas they need to acquire.

        ### CANDIDATE PROFILE (JSON):
        {profile_context}

        ### STRICT RULES:
        1. "gap_skill": Must be an ultra-concise title, maximum 1 to 3 words.
        2. "reason": exact 1 short sentences explaining why this skill is needed for him. Keep it punchy and direct.
        3. "confidence": A float value between 0.0 and 1.0 indicating how certain you are they need this skill.
        4. Return ONLY a JSON list of objects.
        5. QUANTITY LIMIT: You MUST generate exactly 3 to 5 skill gaps. Prioritize the most critical, high-impact skills the user is missing. Do not return more than 5 items.

        ### TARGET JSON SCHEMA:
        [
            {{
                "gap_skill": "Short Skill Name",
                "reason": "Short, direct reason for needing this skill.",
                "confidence": 0.95
            }}
        ]
        """

    @classmethod
    def analyze_and_update_gaps(cls, user_id):
        profile = UserProfile.objects.prefetch_related(
            'education_history', 'experience_history', 'project_history', 'certification_history'
        ).get(user_id=user_id)

        # 1. Build Context & Call Gemini
        context = cls.build_profile_context(profile)
        prompt = cls.generate_skill_gap_prompt(context)
        
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            clean_json = response.text.replace('```json', '').replace('```', '').strip()
            new_gaps = json.loads(clean_json)
            
            # 2. Atomic Database Update (Protecting manual entries)
            # Delete only the AI-generated gaps, keep the user's manual ones
            SkillGap.objects.filter(profile=profile, is_manual=False).delete()
            
            # Insert the new AI insights
            for gap in new_gaps:
                SkillGap.objects.create(
                    profile=profile,
                    gap_skill=gap.get('gap_skill', ''),
                    reason=gap.get('reason', ''),
                    confidence=float(gap.get('confidence', 0.5)),
                    is_manual=False
                )
            logger.info(f"****=======\nSkill gap analysis completed for user {user_id}")
            logger.info(f"****======****\nIdentified gaps: {new_gaps}\n******=============******")
            
        except Exception as e:
            logger.error(f"Failed to run skill gap agent for {user_id}: {e}")