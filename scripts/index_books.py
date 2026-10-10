import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import yaml

from src.chunking.chunker import chunk_sections
from src.ingestion.cleaner import clean_sections
from src.ingestion.loader import load_all_books
from src.vectordb.vector_store import add_chunks, get_collection, reset_collection

with open("config.yaml", encoding="utf-8") as f:
    config = yaml.safe_load(f)

path = config["vectordb"]["path"]
name = config["vectordb"]["collection"]

# python scripts/index_books.py --reset  -> repart d'une base vide
if "--reset" in sys.argv:
    collection = reset_collection(path, name)
    print("Base réinitialisée.")
else:
    collection = get_collection(path, name)

sections = clean_sections(load_all_books("data/books"))
chunks = chunk_sections(
    sections,
    max_chars=config["chunking"]["max_chars"],
    overlap=config["chunking"]["overlap"],
)

if not chunks:
    sys.exit("Aucun chunk à indexer : vérifie data/books/.")

print(f"\n{len(chunks)} chunks à indexer...")
add_chunks(collection, chunks)

print(f"\nTerminé. La base contient {collection.count()} chunks.")