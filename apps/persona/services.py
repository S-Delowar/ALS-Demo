import logging
from apps.chat.models.message import ChatMessage
from apps.persona.tasks import update_user_persona_task
from apps.chat.models import ChatSession
from apps.user_profile.models import UserProfile
from apps.user_profile.tasks import run_chat_insight_profiler_task

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
        if user_msg_count > 0 and user_msg_count % 20 == 0:
            
            # Get last 10 messages for context
            # (We need both user and AI messages to understand context)
            recent_msgs_qs = session.messages.order_by("-created_at")[:4]
            
            # Reverse to get chronological order
            recent_msgs = [
                {"role": m.role, "content": m.content}
                for m in reversed(recent_msgs_qs)
            ]
            
            print(f"Triggering persona update for user {user.id} at message count {user_msg_count}")
            
            # need to pass user id instead of user object
            update_user_persona_task.delay(
                user_id=user.id,
                messages=recent_msgs
            )
            return True
            
    except Exception as e:
        print(f"Failed to trigger persona update: {e}")
        return False 
    
    
# Update goals, preferences, and focus areas based on chat history
class ChatProfilerTriggerService:
    @staticmethod
    def check_and_trigger(user):
        # Fetch ONLY the last 20 USER messages
        recent_msgs = ChatMessage.objects.filter(
            session__user=user,
            role='user'  # <-- Explicitly filter out the AI
        ).order_by('-created_at')[:30]  # Get last 30 user messages
        
        # Reverse into chronological order
        chronological_msgs = reversed(recent_msgs)
        
        # Format the text (No need for "User: / AI:" prefixes anymore)
        chat_history_text = "\n".join([
            f"- {msg.content}"
            for msg in chronological_msgs
        ])
        
        # Fire the async task
        run_chat_insight_profiler_task.delay(user.id, chat_history_text)