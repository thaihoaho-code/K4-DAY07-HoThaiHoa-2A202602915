from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
            self.collection = self.chroma_client.get_or_create_collection(name="my_collection")            
            
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        # Build a normalized stored record for one document
        embedding = self._embedding_fn(doc.content)
        metadata = dict(doc.metadata or {})
        metadata.setdefault("doc_id", doc.id)
        record = {
            "id": doc.id,
            "content": doc.content,
            "embedding": embedding,
            "metadata": metadata,
        }
        return record

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        # Run in-memory similarity search over provided records
        query_embedding = self._embedding_fn(query)
        scored_records = []
        for record in records:
            score = _dot(query_embedding, record["embedding"])
            scored_records.append((score, record))
        scored_records.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "id": record.get("id"),
                "content": record.get("content"),
                "metadata": record.get("metadata", {}),
                "score": score,
            }
            for score, record in scored_records[:top_k]
        ]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        # Embed each doc and add to store
        for doc in docs:
            record = self._make_record(doc)
            if self._use_chroma and self._collection is not None:
                self._collection.add(
                    ids=[record["id"]],
                    documents=[record["content"]],
                    embeddings=[record["embedding"]],
                )
            else:
                self._store.append(record)
            self._next_index += 1

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        # Embed query, compute similarities, return top_k
        if self._use_chroma and self._collection is not None:
            query_embedding = self._embedding_fn(query)
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )
            scored_results = []
            for id_, content, embedding, metadata in zip(
                results["ids"][0],
                results["documents"][0],
                results["embeddings"][0],
                results.get("metadatas", [[{}] * len(results["ids"][0])])[0],
            ):
                scored_results.append({
                    "id": id_,
                    "content": content,
                    "metadata": metadata or {},
                    "score": _dot(query_embedding, embedding),
                })
            scored_results.sort(key=lambda item: item["score"], reverse=True)
            return scored_results
        else:
            return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma and self._collection is not None:
            return self._collection.count()
        else:
            return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        # Filter by metadata, then search among filtered chunks
        if metadata_filter is None:
            filtered_records = self._store
        else:
            filtered_records = [
                record for record in self._store
                if all(record.get("metadata", {}).get(k) == v for k, v in metadata_filter.items())
            ]
        return self._search_records(query, filtered_records, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        original_length = len(self._store)
        self._store = [
            record for record in self._store
            if record.get("metadata", {}).get("doc_id") != doc_id and record.get("id") != doc_id
        ]

        if self._use_chroma and self._collection is not None:
            self._collection.delete(where={"doc_id": doc_id})

        return len(self._store) < original_length
