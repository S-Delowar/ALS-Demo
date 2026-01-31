from apps.chatbot.tools.llm import llm_json_generate


PERSONA_EXTRACTION_PROMPT = """
You are extracting user persona signals from a conversation.

Conversation:
{conversation}

Rules:
- Extract ONLY new or reinforced persona signals
- Do NOT guess or hallucinate
- Ignore small talk
- If no persona info exists, return empty list

Allowed fields:
- profession
- level
- preference
- goal

Return JSON ONLY in this format:
{{
  "signals": [
    {{
      "field": "...",
      "value": "...",
      "confidence": 0.0,
      "evidence": "short quote"
    }}
  ]
}}
"""


def extract_persona_signals(messages: list[dict]) -> list[dict]:
    """
    messages: [{role: 'user|ai', content: str}]
    """

    text = "\n".join(
        f"{m['role']}: {m['content']}" for m in messages
    )

    response = llm_json_generate(
        PERSONA_EXTRACTION_PROMPT.format(conversation=text)
    )

    return response.get("signals", [])
