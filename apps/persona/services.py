import logging
from apps.persona.tasks import update_user_persona_task
from apps.chat.models import ChatSession

logger = logging.getLogger(__name__)

def check_and_trigger_persona_update(session: ChatSession, user):
    """
    Checks if we should run the persona extraction task.
    Trigger rule: Every 5th user message.
    """
    try:
        # Count user messages only
        user_msg_count = session.messages.filter(role="user").count()

        # Trigger on 5th, 10th, 15th message...
        if user_msg_count > 0 and user_msg_count % 5 == 0:
            
            # Get last 10 messages for context
            # (We need both user and AI messages to understand context)
            recent_msgs_qs = session.messages.order_by("-created_at")[:5]
            
            # Reverse to get chronological order
            recent_msgs = [
                {"role": m.role, "content": m.content} 
                for m in reversed(recent_msgs_qs)
            ]
            
            logger.info(f"Triggering persona update for user {user.id} at message count {user_msg_count}")
            
            # need to pass user id instead of user object
            update_user_persona_task.delay(
                user_id=user.id,
                messages=recent_msgs
            )
            return True
            
    except Exception as e:
        logger.info(f"Failed to trigger persona update: {e}")
        return False