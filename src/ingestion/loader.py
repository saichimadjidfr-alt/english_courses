from pathlib import Path

from bs4 import BeautifulSoup
from ebooklib import ITEM_DOCUMENT, epub
from pypdf import PdfReader

SUPPORTED = {".pdf", ".epub", ".txt"}


def load_pdf(path: Path) -> list[dict]:
    reader = PdfReader(str(path))
    sections = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            sections.append(
                {"text": text, "source": path.name, "location": f"page {i}"}
            )
    return sections


def load_epub(path: Path) -> list[dict]:
    book = epub.read_epub(str(path))
    sections = []
    for i, item in enumerate(book.get_items_of_type(ITEM_DOCUMENT), start=1):
        soup = BeautifulSoup(item.get_content(), "html.parser")
        text = soup.get_text(separator="\n")
        if text.strip():
            sections.append(
                {"text": text, "source": path.name, "location": f"section {i}"}
            )
    return sections


def load_txt(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not text.strip():
        return []
    return [{"text": text, "source": path.name, "location": "texte complet"}]


def load_book(path: Path) -> list[dict]:
    path = Path(path)
    ext = path.suffix.lower()
    if ext == ".pdf":
        return load_pdf(path)
    if ext == ".epub":
        return load_epub(path)
    if ext == ".txt":
        return load_txt(path)
    raise ValueError(f"Format non supporté : {ext}")


def load_all_books(folder: str = "data/books") -> list[dict]:
    sections = []
    for path in sorted(Path(folder).iterdir()):
        if path.suffix.lower() in SUPPORTED:
            print(f"Lecture de {path.name}...")
            sections.extend(load_book(path))
    return sections