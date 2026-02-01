from apps.chatbot.graph.state import ChatState


def route_intent(state: ChatState) -> ChatState:
    msg = state["message"].lower()

    if any(k in msg for k in ["recommend", "suggest", "learn", "career", "advice", "profession"]):
        state["intent"] = "recommendation"
    elif any(k in msg for k in ["latest", "today", "current", "recent"]):
        state["intent"] = "web"
    elif any(k in msg for k in ["document", "file", "pdf", "docx", "report", "paper"]):
        state["intent"] = "document"
    else:
        state["intent"] = "direct"

    return state
