import json
import os
import logging
from google import genai
import json
from django.db import transaction
from apps.user_profile.models import LearningInsight, UserProfile
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

logger = logging.getLogger(__name__)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY_LEARNING_INSIGHTS"))


# Schema for the expected response from the LLM. This ensures we can validate and parse the response correctly.
RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "goals": {
            "type": "ARRAY", 
            "items": {
                "type": "OBJECT",
                "properties": {
                    "intent": {"type": "STRING"},
                    "reason": {"type": "STRING"}
                },
                "required": ["intent", "reason"]
            }
        },
        "preferences": {
            "type": "ARRAY", 
            "items": {
                "type": "OBJECT",
                "properties": {
                    "intent": {"type": "STRING"},
                    "reason": {"type": "STRING"}
                },
                "required": ["intent", "reason"]
            }
        },
        "focus_areas": {
            "type": "ARRAY", 
            "items": {
                "type": "OBJECT",
                "properties": {
                    "intent": {"type": "STRING"},
                    "reason": {"type": "STRING"}
                },
                "required": ["intent", "reason"]
            }
        },
    },
    "required": ["goals", "preferences", "focus_areas"],
}


# Analyze User's Chat History to extract learning goals, preferences, and focus areas. Update the UserProfile with new insights.
class ChatProfilerAgentService:
    
    @staticmethod
    def get_current_ai_state(profile):
        """Fetches the CURRENT non-manual insights so the LLM knows what it already generated."""
        insights = LearningInsight.objects.filter(profile=profile, is_manual=False)
        
        state = {"goals": [], "preferences": [], "focus_areas": []}
        for item in insights:
            if item.insight_type == 'goal': state['goals'].append(item.content)
            elif item.insight_type == 'preference': state['preferences'].append(item.content)
            elif item.insight_type == 'focus_area': state['focus_areas'].append(item.content)
            
        return json.dumps(state)

    @staticmethod
    def generate_profiler_prompt(chat_history, current_state):
        return f"""
    You are an AI Learning Profiler. Analyze the user's recent chat history to extract and update their learning goals, preferences, and focus areas. The user could belong to ANY profession, industry, or academic background.

    ### INPUTS
    Current State: {current_state}
    Recent Chat: {chat_history}

    ### EXTRACTION RULES
    1. **Dynamic Capacity**: Extract 0 to 5 items per category. Only include items explicitly supported by the chat. Do not hallucinate fillers.
    2. **State Management**: Merge new insights with the Current State. Discard achieved, abandoned, or lower-priority items to maintain the strict 5-item maximum per category.
    3. **Deduplication**: Consolidate overlapping or duplicate concepts.
    4. **Data Format**: 
       - `intent`: Actionable, ultra-concise string (3-5 words max).
       - `reason`: A brief justification based on the user's input (under 15 words).

    ### EXPECTED OUTPUT
    Return ONLY a JSON object matching this structure. (Note: Examples below show diverse professions to illustrate the expected format):
    {{
        "goals": [
            {{"intent": "Pass NCLEX nursing exam", "reason": "Mentioned studying for upcoming medical boards."}},
            {{"intent": "Scale e-commerce revenue", "reason": "Asked about Q4 holiday marketing strategies."}}
        ],
        "preferences": [
            {{"intent": "Audiobook summaries", "reason": "Stated they prefer listening during their commute."}},
            {{"intent": "Step-by-step case studies", "reason": "Requested real-world examples over theory."}}
        ],
        "focus_areas": [
            {{"intent": "B2B Sales Outreach", "reason": "Discussing cold email conversion rates."}},
            {{"intent": "Supply Chain Logistics", "reason": "Asking about reducing vendor lead times."}}
        ]
    }}
    """

    @classmethod
    def analyze_and_update_insights(cls, user_id, chat_history_text):
        profile = UserProfile.objects.get(user_id=user_id)
        current_state = cls.get_current_ai_state(profile)
        
        prompt = cls.generate_profiler_prompt(chat_history_text, current_state)
        
        try:
            # Using your existing Gemini client
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": RESPONSE_SCHEMA,
                    },
            )
            
            new_insights = json.loads(response.text)
            
            logger.info(f"=====***======\nGenerated new insights for user {user_id}: {new_insights}\n=====***======")
            
            with transaction.atomic():
                # ATOMIC UPDATE: Delete OLD AI-generated insights, protect manual ones
                LearningInsight.objects.filter(profile=profile, is_manual=False).delete()
                
                # Bulk prepare the new records to save DB hits
                insights_to_create = []
                
                # Map the JSON keys to our database choice types
                mapping = {
                    'goals': 'goal',
                    'preferences': 'preference',
                    'focus_areas': 'focus_area'
                }
                
                for json_key, db_type in mapping.items():
                    items = new_insights.get(json_key, [])
                        
                    for item_dict in items:
                        # Extract the dictionary values safely
                        intent_text = item_dict.get('intent', '')[:300]
                        reason_text = item_dict.get('reason', '')[:500]
                        
                        if intent_text:  # Ensure we don't save empty intents
                            insights_to_create.append(
                                LearningInsight(
                                    profile=profile, 
                                    insight_type=db_type, 
                                    content=intent_text, 
                                    reason=reason_text,
                                    is_manual=False
                                )
                            )
                
                # Save all at once
                LearningInsight.objects.bulk_create(insights_to_create, ignore_conflicts=True)
            logger.info(f"Chat profile insights updated for user {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to run chat profiler agent for {user_id}: {e}")