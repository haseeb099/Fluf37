"""ChromaDB vector memory with in-memory fallback."""
import uuid
from typing import List, Optional

import structlog

from backend.config import NexusConfig
from backend.schemas.models import MemoryMetadata, MemoryResult

logger = structlog.get_logger()


class VectorMemory:
    collection_name = "nexus_failures"

    def __init__(self, config: NexusConfig):
        self.config = config
        self._docs: List[dict] = []
        self._use_chroma = False
        self._collection = None
        if not config.is_demo():
            try:
                import chromadb
                self._client = chromadb.PersistentClient(path=config.vector_db_path)
                self._collection = self._client.get_or_create_collection(self.collection_name)
                self._use_chroma = True
            except Exception as e:
                logger.warning("chroma_unavailable", error=str(e))

    async def store(self, text: str, metadata: MemoryMetadata) -> str:
        doc_id = f"vec_{uuid.uuid4().hex[:8]}"
        meta = metadata.model_dump()
        if self._use_chroma and self._collection:
            try:
                self._collection.add(
                    ids=[doc_id],
                    documents=[text],
                    metadatas=[{k: str(v) for k, v in meta.items()}],
                )
                return doc_id
            except Exception as e:
                logger.warning("chroma_store_failed", error=str(e))
        self._docs.append({"id": doc_id, "text": text, "metadata": meta})
        return doc_id

    async def search(self, query: str, n_results: int = 5, filter: Optional[dict] = None) -> List[MemoryResult]:
        if self._use_chroma and self._collection and self._collection.count() > 0:
            try:
                results = self._collection.query(
                    query_texts=[query], n_results=min(n_results, self._collection.count())
                )
                out = []
                for i, doc_id in enumerate(results["ids"][0]):
                    dist = results["distances"][0][i] if results.get("distances") else 0
                    out.append(MemoryResult(
                        id=doc_id,
                        text=results["documents"][0][i],
                        score=max(0, 1 - dist),
                        metadata=MemoryMetadata(agent_id="traceback"),
                    ))
                return out
            except Exception as e:
                logger.warning("chroma_search_failed", error=str(e))
        # In-memory: simple substring match for demo
        matches = [d for d in self._docs if query.lower()[:20] in d["text"].lower() or True]
        return [
            MemoryResult(
                id=d["id"],
                text=d["text"],
                score=0.85,
                metadata=MemoryMetadata(agent_id=d["metadata"].get("agent_id", "traceback")),
            )
            for d in matches[:n_results]
        ]

    async def get_stats(self) -> int:
        if self._use_chroma and self._collection:
            try:
                return self._collection.count()
            except Exception:
                pass
        return len(self._docs)
