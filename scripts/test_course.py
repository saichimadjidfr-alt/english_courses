import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml

from src.course.lesson_generator import generate_course
from src.course.schemas import to_markdown
from src.retrieval.retriever import retrieve

with open("config.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# python scripts/test_course.py "present perfect" B1
topic = sys.argv[1] if len(sys.argv) > 1 else "present perfect"
level = sys.argv[2] if len(sys.argv) > 2 else config["course"]["default_level"]

chunks = retrieve(
    topic,
    path=config["vectordb"]["path"],
    collection_name=config["vectordb"]["collection"],
    top_k=config["retrieval"]["top_k"],
)

print(f"{len(chunks)} extraits trouvés. Génération du cours...\n")
course = generate_course(topic, level, chunks, config)

sources = sorted({f"{c['source']} ({c['location']})" for c in chunks})
markdown = to_markdown(course, topic, level, sources)

print(markdown)

Path("logs").mkdir(exist_ok=True)
Path("logs/last_course.md").write_text(markdown, encoding="utf-8")
print("\nCours sauvegardé dans logs/last_course.md")