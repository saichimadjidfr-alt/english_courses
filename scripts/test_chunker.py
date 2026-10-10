import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml

from src.chunking.chunker import chunk_sections
from src.ingestion.cleaner import clean_sections
from src.ingestion.loader import load_all_books

with open("config.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)

sections = load_all_books("data/books")
sections = clean_sections(sections)
chunks = chunk_sections(
    sections,
    max_chars=config["chunking"]["max_chars"],
    overlap=config["chunking"]["overlap"],
)

print(f"\n{len(sections)} sections propres -> {len(chunks)} chunks")

if chunks:
    avg = sum(len(c["text"]) for c in chunks) / len(chunks)
    print(f"Taille moyenne : {avg:.0f} caractères")

    for c in (chunks[0], chunks[len(chunks) // 2]):
        print("\n" + "=" * 60)
        print(f"{c['source']} ({c['location']})")
        print("=" * 60)
        print(c["text"])