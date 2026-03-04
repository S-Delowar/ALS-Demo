from apps.chatbot.graph.state import ChatState
from apps.persona.models import UserPersona


def persona_loader(state: ChatState) -> ChatState:
    
    print("======*********** Persona Loader Node Called **************======")
    persona = UserPersona.objects.get(user_id=state["user_id"])

    state["persona"] = {
        "name": persona.full_name,
        "profession": persona.profession,
        "level": persona.level,
        "preferences": persona.preferences,
    }

    print(f"Output state of Persona Loader Node: \n\n{state}")
    print("\n\n====*****End of Persona Loader Node*****=======")
    
    return state
