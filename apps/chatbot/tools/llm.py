import json
import logging
from google import genai
from google.genai import types

from apps.chatbot.prompts.system import CORE_SYSTEM_INSTRUCTION

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"

client = genai.Client()

grounding_tool = types.Tool(google_search=types.GoogleSearch())


def llm_json_generate(prompt: str) -> dict:
    """
    Generates JSON output from the LLM based on the given prompt.
    """
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "temperature": 0.3,
        },
    )

    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        print("ERROR: Failed to parse JSON from LLM")
        print("Raw response:", response.text)
        return {}
    
    
    
def llm_generate(message: str, history: list = None, custom_system_instruction: str = None) -> str:
    contents = []
    
    # Convert History
    if history:
        for msg in history:
            contents.append(types.Content(
                role="model" if msg["role"] == "ai" else "user",
                parts=[types.Part.from_text(text=msg["content"])]
            ))

    # Check if history was empty OR if the last message in history is different
    is_duplicated = (
        len(contents) > 0 and 
        contents[-1].role == "user" and 
        contents[-1].parts[0].text == message
    )

    if not is_duplicated:
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=message)]
        ))

    # decide the system instruction to use
    final_instruction = custom_system_instruction if custom_system_instruction else CORE_SYSTEM_INSTRUCTION
    
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            tools=[grounding_tool],
            max_output_tokens=1024,  # <--- LIMITS THE OUTPUT LENGTH
            temperature=0.3,
            system_instruction=final_instruction
        )
    )
    return response.text