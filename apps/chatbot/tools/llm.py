import json
from google import genai

GEMINI_MODEL = "gemini-2.5-flash"

client = genai.Client()


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