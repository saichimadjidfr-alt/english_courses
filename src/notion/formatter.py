import re

MAX_TEXT = 2000  # limite Notion par bloc de texte


def rich_text(text: str) -> list[dict]:
    """Convertit du texte avec **gras** en rich_text Notion (découpé à 2000 caractères)."""
    parts = []
    for piece in re.split(r"(\*\*[^*]+\*\*)", text):
        if not piece:
            continue
        bold = piece.startswith("**") and piece.endswith("**") and len(piece) > 4
        content = piece[2:-2] if bold else piece
        for i in range(0, len(content), MAX_TEXT):
            item = {"type": "text", "text": {"content": content[i : i + MAX_TEXT]}}
            if bold:
                item["annotations"] = {"bold": True}
            parts.append(item)
    return parts or [{"type": "text", "text": {"content": ""}}]


def block(kind: str, text: str, children: list | None = None) -> dict:
    data = {"rich_text": rich_text(text)}
    if children:
        data["children"] = children
    return {"object": "block", "type": kind, kind: data}


def parse_line(line: str) -> dict | None:
    stripped = line.strip()
    if not stripped:
        return None
    if stripped.startswith("# "):
        return None  # le titre H1 devient le titre de la page
    if stripped.startswith("### "):
        return block("heading_3", stripped[4:])
    if stripped.startswith("## "):
        return block("heading_2", stripped[3:])
    if stripped.startswith("#### "):
        return block("heading_3", stripped[5:])
    if re.fullmatch(r"-{3,}", stripped):
        return {"object": "block", "type": "divider", "divider": {}}
    if stripped.startswith("|"):  # tableau markdown -> lignes de liste
        if re.fullmatch(r"[\s|:\-]+", stripped):
            return None
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        return block("bulleted_list_item", " | ".join(cells))
    m = re.match(r"^[-*•]\s+(.*)", stripped)
    if m:
        return block("bulleted_list_item", m.group(1))
    m = re.match(r"^\d+[.)]\s+(.*)", stripped)
    if m:
        return block("numbered_list_item", m.group(1))
    return block("paragraph", stripped)


def parse_lines(lines: list[str]) -> list[dict]:
    return [b for b in (parse_line(l) for l in lines) if b]


def markdown_to_blocks(markdown: str) -> list[dict]:
    lines = markdown.splitlines()
    blocks, i = [], 0
    while i < len(lines):
        # "### Corrigé" -> toggle qui contient les réponses
        if re.match(r"^###\s+Corrig", lines[i].strip()):
            j = i + 1
            while j < len(lines) and not lines[j].lstrip().startswith("#"):
                j += 1
            children = parse_lines(lines[i + 1 : j])
            blocks.append(block("toggle", "Corrigé", children))
            i = j
            continue
        b = parse_line(lines[i])
        if b:
            blocks.append(b)
        i += 1
    return blocks