from arxiv_digest.domain.models import Paper, Topic
from arxiv_digest.infrastructure.arxiv_client import ArxivClient


class Fetcher:
    def __init__(self, client: ArxivClient) -> None:
        self._client = client

    def fetch_topic(
        self,
        topic: Topic,
        days_back: int,
        max_results: int,
    ) -> list[Paper]:
        return self._client.search(topic, days_back, max_results)
