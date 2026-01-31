import logging
from celery import shared_task
from apps.chatbot.tools.llm import llm_json_generate
from apps.memory.persona_memory import save_persona_memory
from apps.memory.weaviate_client import get_weaviate_client
from apps.memory.global_activities import save_global_activity, activities_exist_for_profession
from apps.persona.extractor import extract_persona_signals
from apps.persona.updater import update_persona_from_signals

logger = logging.getLogger(__name__)

GLOBAL_ACTIVITIES_PROMPT = """
You are an expert career analyst.

Generate 10 to 15 common professional activities
for someone with the following profession.

Profession: {profession}

Rules:
- Activities must be realistic and practical
- Avoid buzzwords
- No repetition
- Short and clear phrases

Return JSON ONLY in this format:
{{
  "activities": [
    "activity 1",
    "activity 2"
  ]
}}
"""


@shared_task(bind=True, max_retries=3)
def generate_global_activities_for_profession(self, profession: str):
    """
    Generate and store global activities for a profession.
    Runs ONLY if activities do not already exist.
    """

    # Normalize profession
    profession = profession.strip()

    # Prevent duplicate generation
    if activities_exist_for_profession(profession):
        return f"Activities already exist for {profession}"

    try:
        result = llm_json_generate(
            GLOBAL_ACTIVITIES_PROMPT.format(profession=profession)
        )
        
        logger.info(f"========LLM returned:=====\n\n{result}")
        logger.info("\n\n===========================")
        
        activities = result.get("activities", [])

        if activities:
            with get_weaviate_client() as client:
                for activity in activities:
                    save_global_activity(
                        client=client,  # <--- PASS THE CLIENT HERE
                        text=activity,
                        profession=profession,
                        version="v1"
                    )

        return f"Generated {len(activities)} activities for {profession}"

    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)



# Task: update persona from signals
@shared_task(bind=True, max_retries=3)
def update_user_persona_task(self, user_id:int, messages: list[dict]):
    """
    Background persona intelligence task.
    """
    
    logger.info(f"Starting persona update task for user {user_id}...")

    try:
        signals = extract_persona_signals(messages)

        if not signals:
            return "No persona signals found"

        updated, evidence = update_persona_from_signals(
            user_id=user_id,
            signals=signals
        )
            
        logger.info(f"========*******Evidence snippets: {evidence}")
        if evidence:
            with get_weaviate_client() as client:
                logger.info("========*******Saving evidence to persona memory")
                for ev in evidence:
                    save_persona_memory(
                    client=client,
                    text=ev["text"],
                    user_id=user_id,
                    confidence=ev["confidence"],
                    memory_type=ev["type"],
                )

        return f"Persona updated: {updated}"

    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)