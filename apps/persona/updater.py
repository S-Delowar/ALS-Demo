import logging
from .models import UserPersona

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.7


def update_persona_from_signals(
    user_id: int,
    signals: list[dict]
):
    logger.info(f"Updating persona for user {user_id} with signals: {signals}")
    
    try:
        # Try to get the existing persona
        persona = UserPersona.objects.get(user_id=user_id)
    except UserPersona.DoesNotExist:
        logger.info(f"Persona does not exist for user {user_id}")
        return False, []
    
    updated = False
    evidence_snippets = []

    for signal in signals:
        if signal["confidence"] < CONFIDENCE_THRESHOLD:
            continue

        field = signal["field"]
        value = signal["value"]

        if field == "profession":
            # Only set if currently empty
            if not persona.profession and value:
                persona.profession = value
                updated = True

        elif field == "level":
            # Only set if currently empty
            if not persona.level and value:
                persona.level = value
                updated = True

        elif field == "preference":
            prefs = persona.preferences.get("preferences", [])
            if value not in prefs:
                prefs.append(value)
                persona.preferences["preferences"] = prefs
                updated = True

        elif field == "goal":
            goals = persona.preferences.get("goals", [])
            if value not in goals:
                goals.append(value)
                persona.preferences["goals"] = goals
                updated = True

        if updated:
            evidence_snippets.append({
                "text": signal["evidence"],
                "confidence": signal["confidence"],
                "type": field,
            })

    if updated:
        persona.save()
        logger.info(f"Updated persona for user {user_id}")

    return updated, evidence_snippets
