"""Client for a Text Embeddings Inference Cross-Encoder reranker endpoint."""

import httpx

from app.conf.app_config import RerankerConfig


class RerankerClient:
    """Rerank dense-retrieval candidates with a Cross-Encoder model."""

    def __init__(self, config: RerankerConfig):
        self._url = f"http://{config.host}:{config.port}/rerank"
        self._client = httpx.AsyncClient(timeout=config.timeout_seconds)

    async def rerank(self, query: str, documents: list[str], limit: int) -> list[int]:
        """Return document indexes in descending Cross-Encoder relevance order."""

        if not documents:
            return []
        response = await self._client.post(
            self._url,
            json={"query": query, "texts": documents, "return_text": False},
        )
        response.raise_for_status()
        results = response.json()
        return [item["index"] for item in results[:limit]]

    async def close(self) -> None:
        await self._client.aclose()
