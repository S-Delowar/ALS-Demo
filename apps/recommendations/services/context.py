# apps/recommendations/services/context.py
from apps.memory.global_activities import search_global_activities
from apps.memory.persona_memory import search_persona_memory
from apps.recommendations.services.analyzer import analyze_user_needs

def get_topics_plan(user, profession, chat_history):
    """Gathers user context and fetches topic plans from the LLM."""
    
    # 1. Retrieve Persona Memory
    persona_query = f"Interests, goals, and learning style for {profession}"
    persona_data = search_persona_memory(query=persona_query, user_id=user.id, limit=3)
    persona_text = "\n".join([p.get('text', '') for p in persona_data])

    # 2. Retrieve Global Activities
    global_query = chat_history if len(chat_history) > 50 else f"Trending skills for {profession}"
    global_activities_data = search_global_activities(query=global_query, profession=profession, limit=3)
    global_activities_text = "\n".join([
        item.get('text', '') if isinstance(item, dict) else str(item) 
        for item in global_activities_data
    ])
    
    # 3. Analyze Needs (LLM)
    topics_plan = analyze_user_needs(
        profession=profession, 
        chat_history=chat_history,
        persona=persona_text,
        global_activities=global_activities_text
    )
    
    print(f"================================\n Generated topics plan for user {user.id} and profession {profession}:\n{topics_plan}")
    return topics_plan