from arxiv_digest.domain.models import Paper


class PaperFilter:
    def deduplicate(self, papers: list[Paper]) -> tuple[list[Paper], int]:
        seen: set[str] = set()
        unique: list[Paper] = []
        for p in papers:
            if p.id not in seen:
                seen.add(p.id)
                unique.append(p)
        removed = len(papers) - len(unique)
        return unique, removed

    def filter_quality(self, papers: list[Paper]) -> list[Paper]:
        return [p for p in papers if len(p.abstract.split()) >= 100]

    def run(self, papers: list[Paper]) -> tuple[list[Paper], int]:
        deduped, removed = self.deduplicate(papers)
        filtered = self.filter_quality(deduped)
        return filtered, removed
