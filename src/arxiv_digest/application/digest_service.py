import re
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

from arxiv_digest.application.fetcher import Fetcher
from arxiv_digest.application.filter import PaperFilter
from arxiv_digest.application.prioritizer import Prioritizer
from arxiv_digest.domain.models import Digest, Paper, RoadmapPhase, Topic
from arxiv_digest.infrastructure.arxiv_client import ArxivClient
from arxiv_digest.infrastructure.storage import Storage


def _load_topics(config_dir: Path) -> dict[str, Topic]:
    raw = yaml.safe_load((config_dir / "topics.yaml").read_text())
    categories: list[str] = raw.get("categories", [])
    topics: dict[str, Topic] = {}
    for key, val in raw["topics"].items():
        topics[key] = Topic(
            key=key,
            label=val["label"],
            query=val["query"],
            categories=categories,
        )
    return topics


def _load_roadmap(config_dir: Path) -> tuple[RoadmapPhase, str, int]:
    raw = yaml.safe_load((config_dir / "roadmap.yaml").read_text())
    phase_id: str = raw["current_phase"]
    current_week: int = raw["current_week"]
    phase_data = raw["phases"][phase_id]
    phase = RoadmapPhase(
        id=phase_id,
        name=phase_data["name"],
        current_week=current_week,
        total_weeks=phase_data["total_weeks"],
        priority_topics=phase_data.get("priority_topics", []),
        secondary_topics=phase_data.get("secondary_topics", []),
    )
    return phase, phase_id, current_week


class DigestService:
    def __init__(self, config_dir: Path, output_dir: Path, web_dir: Path) -> None:
        self._config_dir = config_dir
        self._client = ArxivClient()
        self._fetcher = Fetcher(self._client)
        self._filter = PaperFilter()
        self._prioritizer = Prioritizer()
        self._storage = Storage(output_dir, web_dir)

    def run(
        self,
        topics: list[str] | None,
        days_back: int,
        max_per_topic: int,
        output_dir: Path,
    ) -> Digest:
        all_topics = _load_topics(self._config_dir)
        phase, phase_id, current_week = _load_roadmap(self._config_dir)

        selected = (
            {k: v for k, v in all_topics.items() if k in topics}
            if topics
            else all_topics
        )

        all_papers: list[Paper] = []
        errors: list[str] = []

        for key, topic in selected.items():
            try:
                papers = self._fetcher.fetch_topic(topic, days_back, max_per_topic)
                count = len(papers)
                skip = "(skip) " if count == 0 else "  "
                label_padded = topic.label[:20].ljust(20, ".")
                print(f"  {skip}{label_padded} {count} papers")
                all_papers.extend(papers)
            except Exception as e:
                errors.append(f"{key}: {e}")
                print(f"  [ERROR] {key}: {e}")

        filtered, removed = self._filter.run(all_papers)
        if removed:
            print(f"\nDeduplicados: {removed} eliminados")

        tentative = self._prioritizer.build_tentative_list(filtered, phase)

        digest = Digest(
            date=date.today(),
            papers=filtered,
            generated_at=datetime.now(timezone.utc),
            tentative_list=tentative,
        )

        if digest.total() == 0:
            print("\nSin papers nuevos — no se guarda digest vacío.")
        else:
            self._storage.save_digest(digest, phase_id, current_week)
        self._storage.regenerate_html()

        if errors:
            print(f"\n[ADVERTENCIA] Errores en {len(errors)} topic(s): {', '.join(errors)}")

        return digest

    def rebuild_web_only(self) -> None:
        self._storage.regenerate_html()

    def set_week(self, week: int) -> None:
        roadmap_path = self._config_dir / "roadmap.yaml"
        content = roadmap_path.read_text()
        content = re.sub(
            r"^current_week:\s*\d+",
            f"current_week: {week}",
            content,
            flags=re.MULTILINE,
        )
        roadmap_path.write_text(content)
        print(f"Semana actualizada a {week}")
