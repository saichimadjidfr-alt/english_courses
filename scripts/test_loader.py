import sys
from pathlib import Path

# permet d'importer "src" depuis le dossier scripts/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ingestion.loader import load_all_books

sections = load_all_books("data/books")

print(f"\n{len(sections)} sections lues")

if sections:
    first = sections[1]
    print(f"\nLivre : {first['source']} ({first['location']})")
    print("Début du texte :")
    print(first["text"][:500])
else:
    print("Aucune section : vérifie que data/books/ contient un livre.")