import logging
from celery import shared_task
from django.contrib.auth import get_user_model

from apps.chat.models.message import ChatMessage
from apps.recommendations.services.pipeline import run_recommendation_pipeline

logger = logging.getLogger(__name__)
User = get_user_model()

@shared_task
def generate_recommendation_for_user(user_id):
    """
    Task to generate a recommendation for a single user.
    We pass user_id instead of the user object to avoid Celery serialization issues.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found.")
        return
    
    profession = getattr(user, 'profession', 'General Learner')

    # Fetch User's Chat History (SQL)
    recent_messages = ChatMessage.objects.filter(
        session__user=user,
        role='user'
    ).order_by('-created_at')[:10]

    if recent_messages:
        chat_history_text = "\n".join(
            [f"- {msg.content}" for msg in reversed(recent_messages)]
        )
    else:
        chat_history_text = "No recent specific questions asked."

    # Pass data to the orchestrator
    try:
        summary = run_recommendation_pipeline(user, profession, chat_history_text)
        
        logger.info(f"Successfully generated recommendation for user {user.id}")
        return f"Success - User {user.id}"

    except Exception as e:
        logger.error(f"Failed to generate recommendation for user {user.id}: {str(e)}")
        raise e

@shared_task
def trigger_daily_recommendations():
    """
    Master task to run daily. Fetches all active users and queues a task for each.
    """
    # Filter for users who should receive recommendations
    users = User.objects.filter(is_active=True)
    
    for user in users:
        # .delay() queues the task in Redis for your Celery workers to pick up
        generate_recommendation_for_user.delay(user.id)
        
    return f"Queued recommendation tasks for {users.count()} users."