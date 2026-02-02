from duckduckgo_search import DDGS
from apps.chatbot.graph.state import ChatState

def web_search_node(state: ChatState) -> ChatState:
    query = state["message"]
    print(f"--- EXECUTING WEB SEARCH FOR: {query} ---")
    
    try:
        results = []
        with DDGS() as ddgs:
            # Get top 5 results
            search_results = list(ddgs.text(query, max_results=5))
            
            for r in search_results:
                results.append(f"Title: {r['title']}\nLink: {r['href']}\nSnippet: {r['body']}")
                
        state["web_results"] = results
        
    except Exception as e:
        print(f"Web Search Error: {e}")
        state["web_results"] = ["Error performing web search."]

    return state