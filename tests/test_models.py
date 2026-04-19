from datetime import date, datetime

from arxiv_digest.domain.models import Digest, Paper


def _make_paper(id: str, topic_key: str = "agents") -> Paper:
    return Paper(
        id=id, title="T", authors=["A"], abstract="x" * 200,
        published=date.today(), url="u", pdf_url="p",
        categories=["cs.AI"], topic_key=topic_key, topic_label="AI Agents",
    )


def test_by_topic_groups_correctly() -> None:
    papers = [_make_paper("1", "agents"), _make_paper("2", "rag"), _make_paper("3", "agents")]
    digest = Digest(date=date.today(), papers=papers, generated_at=datetime.now())
    by_topic = digest.by_topic()
    assert len(by_topic["agents"]) == 2
    assert len(by_topic["rag"]) == 1


def test_total_no_duplicates() -> None:
    papers = [_make_paper("1"), _make_paper("1"), _make_paper("2")]
    digest = Digest(date=date.today(), papers=papers, generated_at=datetime.now())
    assert digest.total() == 2
