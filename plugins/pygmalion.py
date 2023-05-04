def get_prompt(character_name:str, persona:str, scenario:str, message:str)->str:
    return f"""{character_name}'s Persona: {persona}
{scenario}
<START>
You: {message}
{character_name}:"""