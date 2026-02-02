import json
from google import genai

GEMINI_MODEL = "gemini-2.5-flash"

client = genai.Client()


def call_verification_llm(prompt: str) -> dict:
    """
    Calls the LLM to verify content based on the provided prompt.
    Expects a JSON response with 'is_reliable' and 'reasoning'.
    """
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
        return {"is_reliable": False, "reasoning": "Failed to parse LLM response."}
    
    
    
    
def verify_article(profession, topic, ddg_item, scraped_text):
    """
    Verifies Articles and extracts author/body.
    """
    prompt = f"""
    Context: A {profession} needs to learn about "{topic}".
    Input Title: {ddg_item.get('title')}
    Input Snippet: {ddg_item.get('body')}
    Scraped Text: {scraped_text[:4000]}
    
    Task:
    1. Verify if this article is technically accurate and relevant for the topic.
    2. Extract the Author's name (if not found, use "Unknown").
    
    Output JSON:
    {{
        "is_relevant": true/false,
        "author": "extracted name",
        "platform": "platform name (e.g., Medium, LinkedIn)"
    }}
    """
    return call_verification_llm(prompt)


def verify_course(profession, topic, ddg_item, scraped_text):
    """
    Verifies Courses and extracts instructor, price, and objective list.
    """
    prompt = f"""
    Context: A {profession} needs a course on "{topic}".
    Input Title: {ddg_item.get('title')}
    Input Snippet: {ddg_item.get('body')}
    Scraped Text: {scraped_text[:4000]}
    
    Task:
    1. Verify if this is a legitimate course.
    2. Extract the Instructor/Organization name.
    3. Extract the Price as a number (0.00 for free). If uncertain, use null. 
    4. Extract 4-5 key learning objectives into a list.
    
    Output JSON:
    {{
        "is_relevant": true/false,
        "instructor": "instructor name",
        "price": 10.99,
        "course_objectives": ["objective 1", "objective 2", "objective 3"]
        "platform": "course provider platform name (e.g., Coursera, Udemy)"
    }}
    """
    return call_verification_llm(prompt)


def verify_book(profession, topic, ddg_item, scraped_text):
    """
    Verifies Books and extracts author, publisher, objective list.
    """
    prompt = f"""
    Context: A {profession} needs a book on "{topic}".
    Input Title: {ddg_item.get('title')}
    Input Snippet: {ddg_item.get('body')}
    Scraped Text: {scraped_text[:4000]}
    
    Task:
    1. Verify if this is a relevant technical book.
    2. Extract the Author.
    3. Extract the Publisher.
    4. Summarize the book's content in a brief summary within 150 words.
    
    Output JSON:
    {{
        "is_relevant": true/false,
        "author": "name",
        "publisher": "name",
        "book_summary": "Brief summary of the book content.",
    }}
    """
    return call_verification_llm(prompt)


def verify_video(profession, topic, ddg_item):
    """
    Verifies Videos (No scraping needed, relies on DDG metadata).
    """
    prompt = f"""
    Context: A {profession} needs to learn about "{topic}".
    Video Title: {ddg_item.get('title')}
    Video Description: {ddg_item.get('description')}
    
    Task:
    1. Verify if this video is relevant to the topic.
    2. Ensure it is not a 'short' or entertainment spam.
    
    Output JSON:
    {{
        "is_relevant": true/false
    }}
    """
    return call_verification_llm(prompt)