import json
from google import genai

GEMINI_MODEL = "gemini-2.5-flash"

client = genai.Client()


# # ==========================================
# # MODULE 1: The Strategist (Analyze & Plan)
# # ==========================================
# def analyze_user_needs(profession, chat_history) -> list[dict]:
#     """
#     Analyzes chat history and profession to generate search queries.
#     """
#     prompt = f"""You are an expert educational content strategist.
#     Given the following user context:
#     User Profession: {profession}s
#     Chat History Summary: {chat_history}
    
#     Task: Identify 3 distinct skills/topics this user needs to learn next. if no chat history, base it on profession only.
#     For EACH topic, generate 4 specific DuckDuckGo search queries:
#     1. 'article_query': For a tutorial/blog.
#     2. 'video_query': For a YouTube tutorial.
#     3. 'course_query': For a course (include keywords like 'course').
#     4. 'book_query': For a text-book.

#     Return strictly a JSON list of objects:
#     [
#       {{
#         "topic": "Topic Name",
#         "queries": {{ "article": "...", "video": "...", "course": "...", "book": "..." }}
#       }}
#     ]
#     """
    
#     print("=== Analyzer Prompt ===")
#     print(prompt)

#     response = client.models.generate_content(
#         model=GEMINI_MODEL,
#         contents=prompt,
#         config={
#         "response_mime_type": "application/json",
#     },
#     )

#     try:
#         return json.loads(response.text)
#     except json.JSONDecodeError:
#         print("ERROR: Failed to parse JSON from LLM")
#         print("Raw response:", response.text)
#         return []



def analyze_user_needs(profession, chat_history, persona, global_activities) -> list[dict]:
    """
    Analyzes profession, chat history, persona, and global trends to generate search queries.
    """
    
    prompt = f"""You are an expert educational content strategist.
    
    === USER CONTEXT ===
    1. PROFESSION: {profession}
    
    2. PERSONA (User's specific background/goals):
    {persona if persona else "No specific persona data available."}

    3. RECENT QUESTIONS (User's direct queries):
    {chat_history}

    4. GLOBAL TRENDS (What others in this profession are doing):
    {global_activities if global_activities else "No global trend data available."}

    === TASK ===
    Identify 3 distinct skills/topics this user needs to learn next.
    - Prioritize specific gaps identified in 'RECENT QUESTIONS'.
    - Align recommendations with 'PERSONA' goals.
    - Use 'GLOBAL TRENDS' to suggest cutting-edge or missing standard skills.

    For EACH topic, generate 4 specific DuckDuckGo search queries:
    1. 'article_query': For a tutorial/blog.
    2. 'video_query': For a YouTube tutorial.
    3. 'course_query': For a course (include keywords like 'course').
    4. 'book_query': For a text-book.

    Return strictly a JSON list of objects:
    [
      {{
        "topic": "Topic Name",
        "reason": "Brief reason why this was chosen based on context",
        "queries": {{ "article": "...", "video": "...", "course": "...", "book": "..." }}
      }}
    ]
    """
    
    print("=== ***************Prompt for Analyzer and query generator *************===")
    print(prompt)
    
    print("==================================")

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
        },
    )

    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        print("ERROR: Failed to parse JSON from LLM")
        print("Raw response:", response.text)
        return []