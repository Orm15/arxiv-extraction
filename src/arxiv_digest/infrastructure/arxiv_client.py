import time
from datetime import date, timedelta, datetime, timezone

import arxiv

from arxiv_digest.domain.models import Paper, Topic


class ArxivClient:
    _RATE_LIMIT = 1.5  # seconds between requests
    _MAX_RETRIES = 3
    _RETRY_DELAYS = [2, 4, 8]

    def __init__(self) -> None:
        self._client = arxiv.Client()

    def search(
        self,
        topic: Topic,
        days_back: int,
        max_results: int,
    ) -> list[Paper]:
        cutoff = date.today() - timedelta(days=days_back)
        category_filter = " OR ".join(f"cat:{c}" for c in topic.categories)
        query = f"({topic.query}) AND ({category_filter})"

        for attempt, delay in enumerate(self._RETRY_DELAYS[:self._MAX_RETRIES], 1):
            try:
                search = arxiv.Search(
                    query=query,
                    max_results=max_results,
                    sort_by=arxiv.SortCriterion.SubmittedDate,
                    sort_order=arxiv.SortOrder.Descending,
                )
                papers: list[Paper] = []
                for result in self._client.results(search):
                    published_date = (
                        result.published.date()
                        if isinstance(result.published, datetime)
                        else result.published
                    )
                    if published_date < cutoff:
                        break
                    papers.append(Paper(
                        id=result.entry_id.split("/")[-1],
                        title=result.title,
                        authors=[str(a) for a in result.authors],
                        abstract=result.summary,
                        published=published_date,
                        url=result.entry_id,
                        pdf_url=result.pdf_url or result.entry_id,
                        categories=result.categories,
                        topic_key=topic.key,
                        topic_label=topic.label,
                    ))
                time.sleep(self._RATE_LIMIT)
                return papers
            except Exception:
                if attempt == self._MAX_RETRIES:
                    raise
                time.sleep(delay)
        return []
