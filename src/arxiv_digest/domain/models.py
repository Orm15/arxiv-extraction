from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class Paper:
    id: str                     # arXiv ID (e.g. 2401.12345)
    title: str
    authors: list[str]
    abstract: str
    published: date
    url: str
    pdf_url: str
    categories: list[str]
    topic_key: str
    topic_label: str


@dataclass
class Topic:
    key: str
    label: str
    query: str
    categories: list[str]


@dataclass
class RoadmapPhase:
    id: str
    name: str
    current_week: int
    total_weeks: int
    priority_topics: list[str]
    secondary_topics: list[str]


@dataclass
class TentativePaper:
    paper: Paper
    priority: str               # "alta" | "media" | "baja"
    reason: str


@dataclass
class Digest:
    date: date
    papers: list[Paper]
    generated_at: datetime
    tentative_list: list[TentativePaper] = field(default_factory=list)

    def by_topic(self) -> dict[str, list[Paper]]:
        result: dict[str, list[Paper]] = {}
        for paper in self.papers:
            result.setdefault(paper.topic_key, []).append(paper)
        return result

    def total(self) -> int:
        seen: set[str] = set()
        count = 0
        for p in self.papers:
            if p.id not in seen:
                seen.add(p.id)
                count += 1
        return count
