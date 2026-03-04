# import os

# from google import genai
# from google.genai import types

# from apps.chatbot.graph.state import ChatState

# client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
# grounding_tool = types.Tool(google_search=types.GoogleSearch())


# def web_search_node(state: ChatState) -> ChatState:
#     print("======*********** Web Search Node Called **************======")
    
#     query = state["message"]
#     print(f"--- EXECUTING WEB SEARCH (GEMINI) FOR: {query} ---")

#     try:
#         config = types.GenerateContentConfig(tools=[grounding_tool])
#         response = client.models.generate_content(
#             model="gemini-2.5-flash",
#             contents=query,
#             config=config,
#         )
#         text = response.text if response.text else "No results found."
#         state["web_results"] = [text]
#     except Exception as e:
#         print(f"Web Search Error: {e}")
#         state["web_results"] = ["Error performing web search."]

#     print(f"Output state of Web Search Node: \n\n{state}")
#     print("\n\n====*****End of Web Search Node*****=======")
    
#     return state


# ############################################################################
import os 
from tavily import TavilyClient
from apps.chatbot.graph.state import ChatState
from dotenv import load_dotenv

load_dotenv()

tavily_client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

def web_search_node(state: ChatState) -> ChatState:
    print("======*********** Web Search Node Called **************======")
    
    query = state["message"]
    print(f"--- EXECUTING TAVILY WEB SEARCH FOR: {query} ---")

    try:
        # Perform the search (fetching the top 3 results)
        response = tavily_client.search(query=query, max_results=3)
        
        # Extract the raw snippets
        search_results = []
        for result in response.get("results", []):
            search_results.append(
                f"Source: {result['url']}\nTitle: {result['title']}\nContent: {result['content']}"
            )
            
        # Store the raw text snippets in the state
        state["web_results"] = search_results if search_results else ["No relevant information found online."]
        
    except Exception as e:
        print(f"Web Search Error: {e}")
        state["web_results"] = ["Error performing web search."]

    print(f"Output state of Web Search Node: \n\n{state}")
    print("\n\n====*****End of Web Search Node*****=======")
    
    return state