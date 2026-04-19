from datetime import date

from arxiv_digest.application.filter import PaperFilter
from arxiv_digest.domain.models import Paper


def _make_paper(id: str, abstract: str = "word " * 120) -> Paper:
    return Paper(
        id=id, title="T", authors=["A"], abstract=abstract,
        published=date.today(), url="u", pdf_url="p",
        categories=["cs.AI"], topic_key="agents", topic_label="AI Agents",
    )


def test_deduplication() -> None:
    papers = [_make_paper("1"), _make_paper("1"), _make_paper("2")]
    f = PaperFilter()
    result, removed = f.deduplicate(papers)
    assert removed == 1
    assert len(result) == 2


def test_filter_short_abstract() -> None:
    papers = [_make_paper("1", "short abstract"), _make_paper("2")]
    f = PaperFilter()
    result = f.filter_quality(papers)
    assert len(result) == 1
    assert result[0].id == "2"
