import json
from datetime import date, datetime
from pathlib import Path

from arxiv_digest.domain.models import Digest, Paper, TentativePaper


def _paper_to_dict(p: Paper) -> dict:  # type: ignore[type-arg]
    return {
        "id": p.id,
        "title": p.title,
        "authors": p.authors,
        "abstract": p.abstract,
        "published": p.published.isoformat(),
        "url": p.url,
        "pdf_url": p.pdf_url,
        "categories": p.categories,
        "topic_key": p.topic_key,
        "topic_label": p.topic_label,
    }


def _tentative_to_dict(t: TentativePaper) -> dict:  # type: ignore[type-arg]
    return {
        "paper_id": t.paper.id,
        "priority": t.priority,
        "reason": t.reason,
    }


class Storage:
    def __init__(self, output_dir: Path, web_dir: Path) -> None:
        self.output_dir = output_dir
        self.web_dir = web_dir
        (output_dir / "data").mkdir(parents=True, exist_ok=True)

    def save_digest(self, digest: Digest, current_phase: str, current_week: int) -> Path:
        data_dir = self.output_dir / "data"
        date_str = digest.date.isoformat()
        by_topic = digest.by_topic()

        payload: dict = {  # type: ignore[type-arg]
            "date": date_str,
            "generated_at": digest.generated_at.isoformat(),
            "total": digest.total(),
            "tentative_list": [_tentative_to_dict(t) for t in digest.tentative_list],
            "by_topic": {
                k: [_paper_to_dict(p) for p in v]
                for k, v in by_topic.items()
            },
        }

        out_path = data_dir / f"{date_str}.json"
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))

        self._update_index(date_str, digest.total(), current_phase, current_week)
        return out_path

    def _update_index(
        self,
        date_str: str,
        new_total: int,
        current_phase: str,
        current_week: int,
    ) -> None:
        index_path = self.output_dir / "data" / "index.json"
        if index_path.exists():
            index: dict = json.loads(index_path.read_text())  # type: ignore[type-arg]
        else:
            index = {"dates": [], "total_papers": 0}

        dates: list[str] = index.get("dates", [])
        if date_str not in dates:
            dates.insert(0, date_str)
            index["total_papers"] = index.get("total_papers", 0) + new_total

        index["last_updated"] = datetime.utcnow().isoformat() + "Z"
        index["dates"] = sorted(dates, reverse=True)
        index["current_phase"] = current_phase
        index["current_week"] = current_week

        index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2))

    def regenerate_html(self) -> Path:
        src = self.web_dir / "index.html"
        dst = self.output_dir / "index.html"
        dst.write_text(src.read_text())
        return dst
