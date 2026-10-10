import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

API = "https://api.notion.com/v1"
VERSION = "2022-06-28"


def _headers():
    token = os.getenv("NOTION_TOKEN")
    if not token:
        raise RuntimeError("NOTION_TOKEN manquant dans .env")
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": VERSION,
        "Content-Type": "application/json",
    }


def request(method: str, path: str, payload: dict | None = None, retries: int = 3):
    for _ in range(retries):
        r = requests.request(
            method, f"{API}{path}", headers=_headers(), json=payload, timeout=30
        )
        if r.status_code == 429:  # trop de requêtes : on attend puis on réessaie
            time.sleep(int(r.headers.get("Retry-After", 2)))
            continue
        if not r.ok:
            raise RuntimeError(f"Erreur Notion {r.status_code} : {r.text[:500]}")
        return r.json()
    raise RuntimeError("Notion : trop de requêtes (429), réessaie plus tard.")