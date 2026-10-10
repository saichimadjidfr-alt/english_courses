import copy
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ingestion.cleaner import clean_text, remove_repeated_lines
from src.ingestion.loader import load_all_books

# Optionnel : python scripts/test_cleaner.py 12  -> teste la section n°12
index = int(sys.argv[1]) if len(sys.argv) > 1 else None

raw = load_all_books("data/books")
if not raw:
    sys.exit("Aucune section lue : vérifie data/books/.")

# --- 1. En-têtes / pieds de page détectés et supprimés -------------------
step1 = remove_repeated_lines(copy.deepcopy(raw))

removed = Counter()
for before, after in zip(raw, step1):
    kept = Counter(after["text"].splitlines())
    for line, n in Counter(before["text"].splitlines()).items():
        if line.strip() and n > kept.get(line, 0):
            removed[line.strip()] += n - kept.get(line, 0)

print("=" * 60)
print("1. LIGNES RÉPÉTÉES SUPPRIMÉES (en-têtes, pieds de page)")
print("=" * 60)
if removed:
    for line, n in removed.most_common(15):
        print(f"  {n:4d}x  {line[:70]}")
else:
    print("  Aucune ligne répétée détectée.")
print("  -> Vérifie qu'il n'y a que du bruit ici, pas du vrai contenu.")

# --- 2. Avant / après sur une section -----------------------------------
if index is None:
    index = len(raw) // 2
index = max(0, min(index, len(raw) - 1))

sample_raw = raw[index]["text"]
sample_clean = clean_text(step1[index]["text"])

print("\n" + "=" * 60)
print(f"2. AVANT / APRÈS : {raw[index]['source']} ({raw[index]['location']})")
print("=" * 60)
print("--- AVANT ---")
print(sample_raw[:800])
print("\n--- APRÈS ---")
print(sample_clean[:800])

# --- 3. Contrôles automatiques ------------------------------------------
all_clean = [clean_text(s["text"]) for s in step1]
joined = "\n".join(all_clean)

page_numbers = [
    l for l in joined.splitlines()
    if re.fullmatch(r"(page\s*)?\d{1,4}", l.strip(), re.I)
]
hyphen_breaks = re.findall(r"\w-\n\w", joined)
raw_chars = sum(len(s["text"]) for s in raw)
clean_chars = len(joined)

print("\n" + "=" * 60)
print("3. CONTRÔLES")
print("=" * 60)
print(f"  Sections                    : {len(raw)}")
print(f"  Sections vides après nettoyage : {sum(1 for t in all_clean if not t)}")
print(f"  Caractères avant / après    : {raw_chars} / {clean_chars}")
print(f"  Texte supprimé              : {100 * (1 - clean_chars / raw_chars):.1f} %")
print(f"  Numéros de page restants    : {len(page_numbers)}")
print(f"  Mots coupés restants        : {len(hyphen_breaks)}")