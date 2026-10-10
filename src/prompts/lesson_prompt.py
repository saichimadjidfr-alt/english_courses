SYSTEM_PROMPT = """You are an experienced English teacher who creates short, \
practical 30-minute lessons from textbook extracts.

Rules:
- Base the lesson ONLY on the extracts provided. Do not invent rules that are not supported by them.
- If the extracts do not cover the topic, still return the JSON but keep the lesson short and say so in the explanation.
- Write explanations in {language}. Keep all English examples, exercise questions and answers in English.
- Adapt the difficulty to level {level} (CEFR).
- Be concrete: short explanations, many examples, no filler.
- Reply with ONE valid JSON object and nothing else."""


JSON_FORMAT = """{
  "title": "short lesson title",
  "objectives": ["objective 1", "objective 2"],
  "warmup": "5-minute warm-up: a quick review or a few questions (markdown)",
  "explanation": "10-minute explanation of the rule, with clear points (markdown)",
  "guided_examples": "5 minutes: 4 to 6 example sentences with short comments (markdown)",
  "exercise_instructions": "instructions for a 7-minute exercise",
  "exercise_questions": ["question 1", "question 2", "... 6 to 8 questions"],
  "exercise_answers": ["answer 1", "answer 2", "... same number as questions"],
  "recap": "3-minute recap: the key points to remember (markdown)"
}"""


def build_system_prompt(level: str, language: str) -> str:
    return SYSTEM_PROMPT.format(level=level, language=language)


def build_user_prompt(topic: str, context: str) -> str:
    return f"""Topic of the lesson: {topic}

Textbook extracts:
{context}

Create the lesson as a JSON object with exactly this structure
(all values are strings, except the lists):
{JSON_FORMAT}"""