# from apps.chatbot.graph.state import ChatState


# def route_intent(state: ChatState) -> ChatState:
#     msg = state["message"].lower()

#     if any(k in msg for k in ["recommend", "suggest", "learn", "career", "advice", "profession"]):
#         state["intent"] = "recommendation"
#     elif any(k in msg for k in ["latest", "today", "current", "recent"]):
#         state["intent"] = "web"
#     elif any(k in msg for k in ["document", "file", "pdf", "docx", "report", "paper"]):
#         state["intent"] = "document"
#     else:
#         state["intent"] = "direct"

#     return state



from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from apps.chatbot.graph.state import ChatState

# Define the Structured Output Schema
class RouteQuery(BaseModel):
    "Route user query to the most relevant processing node"
    intent: str = Field(
        description=(
            "Classify the user's intent to route them to the correct agent. "
            "Choose strictly from the following options:\n"
            "- 'recommendation': Use when the user is asking for learning materials, courses, reading lists, study paths, or professional guidance.\n"
            "- 'web': Use when the user asks for up-to-date information, breaking news, or requires searching the internet for current events.\n"
            "- 'document': Use when the user is asking questions about a specific uploaded file, PDF, report, or syllabus.\n"
            "- 'direct': Use for general greetings, casual chat, or questions that can be answered directly without tools."
        )
    )
    
# Initialize model for router.
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# Bind the pydantic model to force the llm to output our exact schema
# Bind the Pydantic model to force the LLM to output our exact schema
structured_llm_router = llm.with_structured_output(RouteQuery)

# Create the Routing Prompt
system_prompt = """You are a highly accurate intent classification router for an AI assistant.
Your job is to read the user's message and categorize it into the correct intent.

Review the descriptions of the intents carefully and make the most logical choice.
Do not answer the user's question; only classify the intent."""

route_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{message}")
])

# Build the Langchain Runnable
intent_chain = route_prompt | structured_llm_router

# Node function
def route_intent(state: ChatState) -> ChatState:
    msg = state["message"]
    
    try:
        result = intent_chain.invoke({"message": msg})
        
        valid_intents = ["recommendation", "web", "document", "direct"]
        if result.intent in valid_intents:
            state["intent"] = result.intent
        else:
            state["intent"] = "direct"
            
    except Exception as e:
        print(f"Routing error: {e}")
        state["intent"] ="direct"
    
    print(f"Output of Router =>  State:\n\n{state}")
    print(f"\n\n####################End of routing")
        
    return state