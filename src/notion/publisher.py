import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from src.notion.formatter import markdown_to_blocks, rich_text
from src.notion.notion_client import request




def get_database() -> dict:
    db_id = os.getenv("NOTION_DATABASE_ID")
    if not db_id:
        raise RuntimeError("NOTION_DATABASE_ID manquant dans .env")
    return request("GET", f"/databases/{db_id}")


def value_for(prop_type: str, value: str) -> dict | None:
    if prop_type == "select":
        return {"select": {"name": value}}
    if prop_type == "rich_text":
        return {"rich_text": rich_text(value)}
    if prop_type == "date":
        return {"date": {"start": value}}
    return None


def build_properties(db_props: dict, title: str, topic: str, level: str, notion_cfg: dict) -> dict:
    title_name = next(n for n, p in db_props.items() if p["type"] == "title")
    props = {title_name: {"title": rich_text(title)}}

    today = datetime.now(ZoneInfo("Europe/Paris")).date().isoformat()
    wanted = [
        ("level_property", level),
        ("topic_property", topic),
        ("date_property", today),
        ("status_property", notion_cfg.get("status_value", "À faire")),
    ]
    for key, value in wanted:
        name = notion_cfg.get(key)
        if not name:
            continue
        if name not in db_props:
            print(f"Avertissement : propriété « {name} » introuvable dans la base, ignorée.")
            continue
        formatted = value_for(db_props[name]["type"], value)
        if formatted is None:
            print(f"Avertissement : type de « {name} » non géré, ignorée.")
            continue
        props[name] = formatted
    return props


def publish_markdown(markdown: str, topic: str, level: str, config: dict) -> str:
    db = get_database()
    m = re.search(r"^#\s+(.+)$", markdown, re.M)
    title = m.group(1).strip() if m else topic

    props = build_properties(db["properties"], title, topic, level, config.get("notion", {}))
    blocks = markdown_to_blocks(markdown)

    # Notion accepte 100 blocs maximum par requête
    page = request(
        "POST",
        "/pages",
        {
            "parent": {"database_id": db["id"]},
            "properties": props,
            "children": blocks[:100],
        },
    )
    for i in range(100, len(blocks), 100):
        request("PATCH", f"/blocks/{page['id']}/children", {"children": blocks[i : i + 100]})

    return page["url"]