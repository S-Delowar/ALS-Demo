from langgraph.graph import StateGraph

from apps.chatbot.graph.nodes.web_search import web_search_node
from .state import ChatState
from .router import route_intent

from .nodes.persona_loader import persona_loader
from .nodes.persona_memory import persona_memory_node
from .nodes.global_activities import global_activities_node
from .nodes.document_retriever import document_node
from .nodes.direct_qa import direct_qa_node
from .nodes.final_llm import final_llm_node


graph = StateGraph(ChatState)

graph.add_node("router", route_intent)
graph.add_node("persona", persona_loader)
graph.add_node("persona_memory", persona_memory_node)
graph.add_node("global", global_activities_node)
graph.add_node("document", document_node)
graph.add_node("direct", direct_qa_node)
graph.add_node("final", final_llm_node)
graph.add_node("web_search", web_search_node)

graph.set_entry_point("router")

graph.add_conditional_edges(
    "router",
    lambda s: s["intent"],
    {
        "direct": "direct",
        "recommendation": "persona",
        "document": "document",
        "web": "web_search",  # optional later
    },
)

graph.add_edge("persona", "persona_memory")
graph.add_edge("persona_memory", "global")
graph.add_edge("global", "final")

graph.add_edge("document", "final")
graph.add_edge("direct", "final")
graph.add_edge("web_search", "final")

chatbot_graph = graph.compile()
