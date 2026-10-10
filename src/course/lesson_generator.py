import json

from pydantic import ValidationError

from src.course.schemas import Course
from src.llm.llm_client import chat_json
from src.prompts.lesson_prompt import build_system_prompt, build_user_prompt


def build_context(chunks: list[dict], max_chars: int) -> str:
    parts, total = [], 0
    for c in chunks:
        block = f"[{c['source']}, {c['location']}]\n{c['text']}"
        if total + len(block) > max_chars:
            break
        parts.append(block)
        total += len(block)
    return "\n\n---\n\n".join(parts)


def generate_course(topic: str, level: str, chunks: list[dict], config: dict, retries: int = 3) -> Course:
    context = build_context(chunks, config["course"]["max_context_chars"])
    system = build_system_prompt(level, config["course"]["explanation_language"])
    user = build_user_prompt(topic, context)

    last_error = None
    for attempt in range(1, retries + 1):
        prompt = user
        if last_error:
            prompt += f"\n\nYour previous answer was invalid: {last_error}\nReturn a valid JSON object only."

        raw = chat_json(system, prompt, config["llm"])
        try:
            return Course.model_validate(json.loads(raw))
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = str(e)[:500]
            print(f"Essai {attempt}/{retries} : format invalide, nouvelle tentative...")

    raise RuntimeError(f"Impossible d'obtenir un cours valide. Dernière erreur : {last_error}")