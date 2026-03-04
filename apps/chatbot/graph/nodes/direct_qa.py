from apps.chatbot.graph.state import ChatState
from apps.chatbot.prompts.system import CORE_SYSTEM_INSTRUCTION
from apps.chatbot.tools.llm import llm_generate


def direct_qa_node(state: ChatState) -> ChatState:
    
    print("======*********** Direct QA Node Called **************======")
    
    user_persona = state.get("persona", {})
    
    dynamic_instruction = CORE_SYSTEM_INSTRUCTION
    
    if user_persona:
        if user_persona:
            dynamic_instruction += "\n\n--- USER CONTEXT ---\n"
            dynamic_instruction += f"Name: {user_persona.get('name', 'Unknown')}\n"
            dynamic_instruction += f"Profession: {user_persona.get('level', '')} {user_persona.get('profession', '')}\n"
            
            # prefs = user_persona.get("preferences", {})
            # if "goals" in prefs:
            #     dynamic_instruction += f"Goals: {', '.join(prefs['goals'])}\n"
    
    state["final_answer"] = llm_generate(
        message=state["message"],
        history=state.get("history", []),
        custom_system_instruction=dynamic_instruction 
    )
    
    print(f"Output state of Direct QA Node: \n\n{state}")
    print("\n\n====*****End of Direct_QA node*****=======")
    return state
