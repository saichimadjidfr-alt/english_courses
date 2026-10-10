import re
from collections import Counter


def remove_repeated_lines(sections, min_sections=5, ratio=0.3):
    """Supprime les en-têtes / pieds de page qui reviennent sur beaucoup de pages."""
    by_source = {}
    for s in sections:
        by_source.setdefault(s["source"], []).append(s)

    for secs in by_source.values():
        if len(secs) < min_sections:
            continue

        counter = Counter()
        for s in secs:
            keys = {
                re.sub(r"\d+", "#", line.strip())
                for line in s["text"].splitlines()
                if line.strip()
            }
            counter.update(keys)

        repeated = {
            key
            for key, count in counter.items()
            if count / len(secs) >= ratio and len(key) < 80
        }

        for s in secs:
            kept = [
                line
                for line in s["text"].splitlines()
                if re.sub(r"\d+", "#", line.strip()) not in repeated
            ]
            s["text"] = "\n".join(kept)
    return sections


def clean_text(text: str) -> str:
    text = text.replace("\r", "")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)  # mots coupés en fin de ligne

    lines = [line.strip() for line in text.split("\n")]
    # lignes qui ne contiennent qu'un numéro de page
    lines = [l for l in lines if not re.fullmatch(r"(page\s*)?\d{1,4}", l, re.I)]

    paragraphs = []
    current = ""
    for line in lines:
        if not line:
            if current:
                paragraphs.append(current)
                current = ""
            continue
        # on recolle les lignes tant que la phrase n'est pas finie
        if current and not re.search(r"[.!?:;\"')]$", current):
            current += " " + line
        else:
            if current:
                paragraphs.append(current)
            current = line
    if current:
        paragraphs.append(current)

    text = "\n\n".join(paragraphs)
    return re.sub(r"[ \t]+", " ", text).strip()


def clean_sections(sections):
    sections = remove_repeated_lines(sections)
    cleaned = []
    for s in sections:
        text = clean_text(s["text"])
        if text:
            cleaned.append({**s, "text": text})
    return cleaned