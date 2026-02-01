from apps.chatbot.graph.state import ChatState
from apps.chatbot.tools.llm import llm_generate


def final_llm_node(state: ChatState) -> ChatState:
    context = []

    if state.get("persona"):
        context.append(f"User persona: {state['persona']}")

    if state.get("persona_memory"):
        context.append("User preferences:\n" + "\n".join(state["persona_memory"]))

    if state.get("global_activities"):
        context.append("Relevant professional context:\n" + "\n".join(state["global_activities"]))

    if state.get("documents"):
        context.append("Relevant documents:\n" + "\n".join(state["documents"]))

    prompt = "\n\n".join(context + [state["message"]])

    state["final_answer"] = llm_generate(
        prompt,
        history=state["history"],
    )

    return state
