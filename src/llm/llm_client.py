import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def chat_json(system: str, user: str, llm_config: dict) -> str:
    """Appelle Groq et renvoie le texte de la réponse (un JSON)."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model=llm_config["model"],
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=llm_config["max_tokens"],
        reasoning_effort=llm_config["reasoning_effort"],
        response_format={"type": "json_object"},
        temperature=0.4,
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError(
            "Réponse vide : augmente max_tokens dans config.yaml "
            "(le raisonnement a consommé tous les tokens)."
        )
    return content