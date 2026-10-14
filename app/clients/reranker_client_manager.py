"""Application-scoped manager for the Cross-Encoder reranker client."""

from app.clients.reranker_client import RerankerClient
from app.conf.app_config import app_config


class RerankerClientManager:
    def __init__(self) -> None:
        self.client: RerankerClient | None = None

    def init(self) -> None:
        self.client = RerankerClient(app_config.reranker)

    async def close(self) -> None:
        if self.client:
            await self.client.close()
            self.client = None


reranker_client_manager = RerankerClientManager()
