from pydantic import BaseModel, Field, model_validator

# Durées fixées par le code (total = 30 min)
DURATIONS = {
    "warmup": 5,
    "explanation": 10,
    "guided_examples": 5,
    "exercise": 7,
    "recap": 3,
}


class Course(BaseModel):
    title: str
    objectives: list[str] = Field(min_length=2)
    warmup: str
    explanation: str
    guided_examples: str
    exercise_instructions: str
    exercise_questions: list[str] = Field(min_length=3)
    exercise_answers: list[str]
    recap: str

    @model_validator(mode="after")
    def check_answers(self):
        if len(self.exercise_answers) != len(self.exercise_questions):
            raise ValueError(
                "exercise_answers doit contenir autant d'éléments que exercise_questions"
            )
        return self


def to_markdown(course: Course, topic: str, level: str, sources: list[str]) -> str:
    d = DURATIONS
    objectives = "\n".join(f"- {o}" for o in course.objectives)
    questions = "\n".join(f"{i}. {q}" for i, q in enumerate(course.exercise_questions, 1))
    answers = "\n".join(f"{i}. {a}" for i, a in enumerate(course.exercise_answers, 1))
    src = "\n".join(f"- {s}" for s in sources)

    return f"""# {course.title}

**Niveau :** {level} | **Thème :** {topic} | **Durée :** {sum(d.values())} min

## Objectifs
{objectives}

## 1. Warm-up ({d['warmup']} min)
{course.warmup}

## 2. Explication ({d['explanation']} min)
{course.explanation}

## 3. Exemples guidés ({d['guided_examples']} min)
{course.guided_examples}

## 4. Exercice ({d['exercise']} min)
{course.exercise_instructions}

{questions}

### Corrigé
{answers}

## 5. Récap ({d['recap']} min)
{course.recap}

## Sources
{src}
"""