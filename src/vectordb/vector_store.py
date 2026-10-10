import chromadb


def get_collection(path: str, name: str):
    client = chromadb.PersistentClient(path=path)
    return client.get_or_create_collection(name=name)


def reset_collection(path: str, name: str):
    client = chromadb.PersistentClient(path=path)
    try:
        client.delete_collection(name)
    except Exception:
        pass  # la collection n'existait pas encore
    return client.get_or_create_collection(name=name)


def add_chunks(collection, chunks: list[dict], batch_size: int = 100):
    """Ajoute (ou met à jour) les chunks par lots. Relancer le script ne crée pas de doublons."""
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        collection.upsert(
            ids=[c["id"] for c in batch],
            documents=[c["text"] for c in batch],
            metadatas=[
                {"source": c["source"], "location": c["location"]} for c in batch
            ],
        )
        print(f"  {min(i + batch_size, len(chunks))}/{len(chunks)} chunks indexés")


def search(collection, query: str, top_k: int = 5):
    return collection.query(query_texts=[query], n_results=top_k)