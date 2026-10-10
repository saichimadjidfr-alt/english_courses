import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml

from src.notion.publisher import get_database, publish_markdown

with open("config.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# 1. Test de connexion
db = get_database()
name = db["title"][0]["plain_text"] if db["title"] else "(sans titre)"
print(f"Connexion OK. Base : {name}")
print("Propriétés :", ", ".join(f"{n} ({p['type']})" for n, p in db["properties"].items()))

# 2. Publication du dernier cours généré par test_course.py
path = Path("logs/last_course.md")
if not path.exists():
    sys.exit("\nlogs/last_course.md introuvable : lance d'abord scripts/test_course.py")

markdown = path.read_text(encoding="utf-8")
m = re.search(r"\*\*Niveau :\*\* (\S+) \| \*\*Thème :\*\* (.+?) \|", markdown)
level, topic = (m.group(1), m.group(2)) if m else (config["course"]["default_level"], "test")

url = publish_markdown(markdown, topic, level, config)
print(f"\nPage créée : {url}")