from datetime import date

from arxiv_digest.application.prioritizer import Prioritizer
from arxiv_digest.domain.models import Paper, RoadmapPhase


def _make_paper(id: str, topic_key: str) -> Paper:
    return Paper(
        id=id, title="T", authors=["A"], abstract="x" * 200,
        published=date.today(), url="u", pdf_url="p",
        categories=["cs.AI"], topic_key=topic_key, topic_label=topic_key,
    )


def _phase() -> RoadmapPhase:
    return RoadmapPhase(
        id="fase_1", name="F1", current_week=1, total_weeks=6,
        priority_topics=["agents"], secondary_topics=["rag"],
    )


def test_priority_alta() -> None:
    papers = [_make_paper("1", "agents")]
    result = Prioritizer().build_tentative_list(papers, _phase())
    assert result[0].priority == "alta"


def test_max_items() -> None:
    papers = [_make_paper(str(i), "agents") for i in range(10)]
    result = Prioritizer().build_tentative_list(papers, _phase(), max_items=3)
    assert len(result) <= 3


def test_low_priority_not_in_tentative() -> None:
    papers = [_make_paper("1", "multimodal")]
    result = Prioritizer().build_tentative_list(papers, _phase())
    assert len(result) == 0
