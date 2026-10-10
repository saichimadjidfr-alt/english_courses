from src.vectordb.vector_store import get_collection


def retrieve(query: str, path: str, collection_name: str, top_k: int = 5, source: str | None = None):
    """Renvoie les chunks les plus proches de la requête.

    source : nom exact d'un livre pour limiter la recherche à celui-ci (optionnel).
    """
    collection = get_collection(path, collection_name)
    if collection.count() == 0:
        raise RuntimeError("La base est vide : lance d'abord scripts/index_books.py")

    kwargs = {"query_texts": [query], "n_results": top_k}
    if source:
        kwargs["where"] = {"source": source}

    result = collection.query(**kwargs)

    chunks = []
    for text, meta, distance in zip(
        result["documents"][0], result["metadatas"][0], result["distances"][0]
    ):
        chunks.append(
            {
                "text": text,
                "source": meta["source"],
                "location": meta["location"],
                "distance": distance,  # plus c'est petit, plus c'est proche
            }
        )
    return chunks