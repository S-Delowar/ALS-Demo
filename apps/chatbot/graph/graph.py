from langgraph.graph import StateGraph

from apps.chatbot.graph.nodes.web_search import web_search_node
from .state import ChatState
from .router import route_intent

from .nodes.persona_loader import persona_loader
from .nodes.persona_memory import persona_memory_node
from .nodes.global_activities import global_activities_node
from .nodes.document_node import document_node
from .nodes.direct_qa import direct_qa_node
from .nodes.final_llm import final_llm_node

graph = StateGraph(ChatState)

# --- 1. Add Nodes ---
graph.add_node("router", route_intent)
graph.add_node("persona", persona_loader)
graph.add_node("persona_memory", persona_memory_node)
graph.add_node("global", global_activities_node)
graph.add_node("document", document_node)
graph.add_node("direct", direct_qa_node)
graph.add_node("final", final_llm_node)
graph.add_node("web_search", web_search_node)

# --- 2. Change Entry Point ---
# OLD: graph.set_entry_point("router")
# NEW: Start with persona_loader so it runs every time
graph.set_entry_point("persona") 

# --- 3. Connect Persona to Router ---
# After persona loads, we move to the router to decide the intent
graph.add_edge("persona", "router") 

# --- 4. Update Router Logic ---
graph.add_conditional_edges(
    "router",
    lambda s: s["intent"],
    {
        "direct": "direct",
        "recommendation": "persona_memory", 
        "document": "document",
        "web": "web_search",  
    },
)

# --- 5. Define Remaining Edges ---
graph.add_edge("persona_memory", "global")
graph.add_edge("global", "web_search")

graph.add_edge("document", "final")
# graph.add_edge("direct", "final")
graph.add_edge("web_search", "final")

chatbot_graph = graph.compile()