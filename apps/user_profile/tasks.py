from celery import shared_task

from apps.user_profile.services.skill_gap_service import SkillGapAgentService
from .services.resume_service import ResumeService
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_resume_task(user_id, file_path):
    try:
        service = ResumeService()
        # 1. Extract
        text = service.extract_text_from_pdf(file_path)
        if not text:
            return "No text found in PDF"
        # 2. Parse
        json_data = service.call_gemini_parser(text)
        # 3. Save
        service.update_profile_from_json(user_id, json_data)
        
        logger.info(f"=============\n\nSuccessfully processed resume for user {user_id}==============\n\n")
        logger.debug(f"============\n\nExtracted JSON: {json_data}===================\n\n")
        logger.info(f"==============\n\nProfile updated for user {user_id}==============n\n")
        
        return f"Profile updated for user {user_id}"
    except Exception as e:
        logger.error(f"Task failed: {e}")
        return str(e)
    
    
@shared_task
def run_skill_gap_analysis_task(user_id):
    try:
        SkillGapAgentService.analyze_and_update_gaps(user_id)
        return f"Skill gaps updated for user {user_id}"
    except Exception as e:
        logger.error(f"Skill Gap Task failed: {e}")
        return str(e)