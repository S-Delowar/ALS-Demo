import json
from apps.chatbot.graph.state import ChatState
from apps.chatbot.tools.llm import llm_generate
from apps.chatbot.prompts.system import CORE_SYSTEM_INSTRUCTION

def final_llm_node(state: ChatState) -> ChatState:
    context_blocks = []

    # 1. Handle User Persona (Django Model or Dict)
    # We format this nicely so the LLM understands who it is talking to.
    if state.get("persona"):
        p = state["persona"]
        
        # Check if it's a Django model object (has attributes) or a dict (has keys)
        # We access attributes safely based on your UserPersona model
        profession = getattr(p, "profession", None) or p.get("profession", "Unknown")
        level = getattr(p, "level", None) or p.get("level", "Unknown")
        
        # Handle 'preferences' JSONField (which might be a dict or string)
        prefs = getattr(p, "preferences", {}) or p.get("preferences", {})
        if isinstance(prefs, dict):
            prefs_str = json.dumps(prefs, indent=2)
        else:
            prefs_str = str(prefs)

        persona_str = (
            f"PROFESSION: {profession}\n"
            f"EXPERIENCE LEVEL: {level}\n"
            f"EXPLICIT PREFERENCES: {prefs_str}"
        )
        context_blocks.append(f"### CURRENT USER PROFILE\n{persona_str}")

    # 2. Handle Persona Memory (Weaviate Results)
    # Your save_persona_memory function uses the key "text".
    if state.get("persona_memory"):
        memory_strings = []
        for mem in state["persona_memory"]:
            if isinstance(mem, dict):
                # We specifically look for 'text' because that is how you saved it
                content = mem.get("text", str(mem))
                memory_strings.append(f"- {content}")
            elif isinstance(mem, str):
                memory_strings.append(f"- {mem}")
            else:
                # Fallback for Weaviate object wrapper if not converted to dict
                memory_strings.append(f"- {str(mem)}")
        
        if memory_strings:
            context_blocks.append("### RELEVANT MEMORIES\n" + "\n".join(memory_strings))

    # 3. Handle Global Activities (Professional Context)
    if state.get("global_activities"):
        # Assuming these are just strings (as per your earlier search function)
        # If they are dicts, use the same logic as above.
        activity_strings = []
        for act in state["global_activities"]:
            if isinstance(act, dict):
                activity_strings.append(f"- {act.get('text', str(act))}")
            else:
                activity_strings.append(f"- {str(act)}")
                
        context_blocks.append("### PROFESSIONAL CONTEXT\n" + "\n".join(activity_strings))

    # 4. Handle Documents (RAG)
    if state.get("documents"):
        doc_strings = []
        for doc in state["documents"]:
            # LangChain documents usually use 'page_content'
            if isinstance(doc, dict):
                doc_strings.append(f"- {doc.get('page_content', doc.get('text', str(doc)))}")
            else:
                # If it is a Document object
                doc_strings.append(f"- {getattr(doc, 'page_content', str(doc))}")
                
        context_blocks.append("### RETRIEVED DOCUMENTS\n" + "\n".join(doc_strings))

    # Handle Web Results
    if state.get("web_results"):
        web_content = "\n\n".join(state["web_results"])
        context_blocks.append(f"### LIVE WEB SEARCH RESULTS\n{web_content}")
        
    # Combine Context + User Question
    # We add the "User Message" clearly at the end
    full_prompt = "\n\n".join(context_blocks + [f"### USER REQUEST\n{state['message']}"])

    # Call LLM
    # Note: We do not need to convert 'history' here because llm_generate handles it
    state["final_answer"] = llm_generate(
        message=full_prompt,
        history=state["history"],
        # system_instruction=CORE_SYSTEM_INSTRUCTION
    )

    return state