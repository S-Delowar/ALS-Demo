from apps.chatbot.graph.state import ChatState
from apps.chatbot.tools.llm import llm_generate


def direct_qa_node(state: ChatState) -> ChatState:
    
    print("======*********** Direct QA Node Called **************======")
    state["final_answer"] = llm_generate(
        state["message"],
        history=state["history"],
    )
    return state
