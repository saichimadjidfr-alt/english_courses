import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml

from src.retrieval.retriever import retrieve

with open("config.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# python scripts/test_retriever.py "present perfect"
query = " ".join(sys.argv[1:]) or "present perfect"

results = retrieve(
    query,
    path=config["vectordb"]["path"],
    collection_name=config["vectordb"]["collection"],
    top_k=config["retrieval"]["top_k"],
)

print(f"\nRecherche : « {query} »\n")

for i, r in enumerate(results, start=1):
    print("=" * 60)
    print(f"#{i}  {r['source']} ({r['location']})  distance = {r['distance']:.3f}")
    print("=" * 60)
    print(r["text"][:600])
    print()