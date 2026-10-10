import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)  # les chemins relatifs marchent quel que soit l'endroit où on lance

import yaml

from src.course.lesson_generator import generate_course
from src.course.schemas import to_markdown
from src.notion.publisher import publish_markdown
from src.retrieval.retriever import retrieve

STATE = Path("data/state/progress.json")
CURRICULUM = Path("data/curriculum.yaml")


def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"done": []}


def save_state(state: dict):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    with open("config.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    force = "--force" in sys.argv or bool(os.getenv("FORCE_RUN"))
    now = datetime.now(ZoneInfo("Europe/Paris"))
    today = now.date().isoformat()
    state = load_state()

    if not force:
        if now.hour < 9:
            print(f"Il est {now:%H:%M} à Paris, avant 9h : rien à faire.")
            return
        if any(e["date"] == today and e["status"] == "published" for e in state["done"]):
            print("Le cours du jour est déjà publié.")
            return

    curriculum = yaml.safe_load(CURRICULUM.read_text(encoding="utf-8")) or []
    done_keys = {(e["topic"], e["level"]) for e in state["done"]}
    pending = [
        {"topic": t["topic"], "level": t.get("level", config["course"]["default_level"])}
        for t in curriculum
    ]
    pending = [t for t in pending if (t["topic"], t["level"]) not in done_keys]

    if not pending:
        sys.exit("Curriculum terminé : ajoute des thèmes dans data/curriculum.yaml")

    max_distance = config["retrieval"].get("max_distance", 1.2)

    for item in pending:
        topic, level = item["topic"], item["level"]
        print(f"\nThème : {topic} ({level})")

        chunks = retrieve(
            topic,
            path=config["vectordb"]["path"],
            collection_name=config["vectordb"]["collection"],
            top_k=config["retrieval"]["top_k"],
        )
        chunks = [c for c in chunks if c["distance"] <= max_distance]

        if not chunks:
            print("Thème absent des livres, on passe au suivant.")
            state["done"].append(
                {"topic": topic, "level": level, "date": today, "status": "skipped"}
            )
            save_state(state)
            continue

        course = generate_course(topic, level, chunks, config)
        sources = sorted({f"{c['source']} ({c['location']})" for c in chunks})
        markdown = to_markdown(course, topic, level, sources)

        url = publish_markdown(markdown, topic, level, config)
        print(f"Publié : {url}")

        state["done"].append(
            {"topic": topic, "level": level, "date": today, "status": "published", "url": url}
        )
        save_state(state)
        return

    print("Aucun thème du curriculum n'a pu être traité (tous absents des livres).")


if __name__ == "__main__":
    main()