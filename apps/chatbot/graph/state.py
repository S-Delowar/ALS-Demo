from typing import NotRequired, TypedDict, List, Optional


class ChatState(TypedDict):
    user_id: int
    session_id: int
    message: str
    history: List[dict]
    intent: str 
    final_answer: Optional[str]
    # --- Optional Fields ---
    persona: NotRequired[Optional[dict]]
    persona_memory: NotRequired[List[str]]
    global_activities: NotRequired[List[str]]
    documents: NotRequired[List[str]]