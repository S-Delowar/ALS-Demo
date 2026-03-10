from datetime import timedelta
import logging
from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.chat.models.message import ChatMessage
# from apps.recommendations.services.pipeline import run_recommendation_pipeline

from apps.recommendations.services.pipeline_02 import run_full_recommendation_pipeline

logger = logging.getLogger(__name__)
User = get_user_model()

# @shared_task
# def generate_recommendation_for_user(user_id):
#     """
#     Task to generate a recommendation for a single user.
#     We pass user_id instead of the user object to avoid Celery serialization issues.
#     """
#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         logger.error(f"User {user_id} not found.")
#         return
    
#     profession = getattr(user, 'profession', 'General Learner')

#     # Fetch User's Chat History (SQL)
#     recent_messages = ChatMessage.objects.filter(
#         session__user=user,
#         role='user'
#     ).order_by('-created_at')[:10]

#     if recent_messages:
#         chat_history_text = "\n".join(
#             [f"- {msg.content}" for msg in reversed(recent_messages)]
#         )
#     else:
#         chat_history_text = "No recent specific questions asked."

#     # Pass data to the orchestrator
#     try:
#         summary = run_recommendation_pipeline(user, profession, chat_history_text)
        
#         logger.info(f"Successfully generated recommendation for user {user.id}")
#         return f"Success - User {user.id}"

#     except Exception as e:
#         logger.error(f"Failed to generate recommendation for user {user.id}: {str(e)}")
#         raise e

# @shared_task
# def trigger_daily_recommendations():
#     """
#     Master task to run daily. Fetches all active users and queues a task for each.
#     """
#     # Filter for users who should receive recommendations
#     users = User.objects.filter(is_active=True)
    
#     for user in users:
#         # .delay() queues the task in Redis for your Celery workers to pick up
#         generate_recommendation_for_user.delay(user.id)
        
#     return f"Queued recommendation tasks for {users.count()} users."




@shared_task(bind=True, max_retries=3)
def generate_user_recommendations_task(self, user_id):
    """
    Universal task to generate recommendations. 
    Can be called on signup or triggered manually later.
    """
    try:
        # 1. Fetch the user and profession
        user = User.objects.get(id=user_id)
        profession = getattr(user, 'profession', '') or 'general'

        # 2. Fetch recent chat history (Using our 20-hour / 50-message limit rule)
        time_threshold = timezone.now() - timedelta(hours=20)
        MAX_MESSAGES = 50

        recent_qs = ChatMessage.objects.filter(
            session__user=user,
            role='user',
            created_at__gte=time_threshold
        ).order_by('-created_at')[:MAX_MESSAGES]

        # Reverse in memory to ensure chronological order for Gemini 2.5 Flash
        recent_user_messages = list(recent_qs)[::-1]

        # 3. Format the history text
        if recent_user_messages:
            chat_history_text = "\n".join(
                [f"- {msg.content}" for msg in recent_user_messages]
            )
        else:
            # This will automatically be the case for brand new signups
            chat_history_text = "No recent specific questions asked."

        # 4. Execute the ThreadPoolExecutor pipeline
        summary = run_full_recommendation_pipeline(user, profession, chat_history_text)
        
        return summary

    except Exception as exc:
        self.retry(exc=exc, countdown=2 ** self.request.retries)