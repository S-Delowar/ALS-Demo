import os

from google import genai
from google.genai import types

from apps.chatbot.graph.state import ChatState

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
grounding_tool = types.Tool(google_search=types.GoogleSearch())


def web_search_node(state: ChatState) -> ChatState:
    query = state["message"]
    print(f"--- EXECUTING WEB SEARCH (GEMINI) FOR: {query} ---")

    try:
        config = types.GenerateContentConfig(tools=[grounding_tool])
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=query,
            config=config,
        )
        text = response.text if response.text else "No results found."
        state["web_results"] = [text]
    except Exception as e:
        print(f"Web Search Error: {e}")
        state["web_results"] = ["Error performing web search."]

    return state
