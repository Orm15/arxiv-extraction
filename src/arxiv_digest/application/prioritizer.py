from arxiv_digest.domain.models import Paper, RoadmapPhase, TentativePaper


class Prioritizer:
    def build_tentative_list(
        self,
        papers: list[Paper],
        phase: RoadmapPhase,
        max_items: int = 3,
    ) -> list[TentativePaper]:
        high: list[TentativePaper] = []
        medium: list[TentativePaper] = []

        for paper in sorted(papers, key=lambda p: p.published, reverse=True):
            if paper.topic_key in phase.priority_topics:
                high.append(TentativePaper(
                    paper=paper,
                    priority="alta",
                    reason=f"tu semana actual — {paper.topic_label}",
                ))
            elif paper.topic_key in phase.secondary_topics:
                medium.append(TentativePaper(
                    paper=paper,
                    priority="media",
                    reason=f"próxima prioridad — {paper.topic_label}",
                ))

        max_high = max_items - 1  # reserve 1 slot for medium
        result = high[:max_high]
        remaining = max_items - len(result)
        result += medium[:remaining]
        return result[:max_items]
