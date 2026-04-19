import argparse
import datetime
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="arxiv-digest",
        description="arXiv AI Digest — fetch, filter, publish",
    )
    parser.add_argument("--days", type=int, default=1, help="Días hacia atrás")
    parser.add_argument("--topics", nargs="+", help="Topics a procesar")
    parser.add_argument("--max-per-topic", type=int, default=20)
    parser.add_argument("--rebuild-web-only", action="store_true")
    parser.add_argument("--set-week", type=int, metavar="N")

    args = parser.parse_args()

    root = Path(__file__).parent.parent.parent
    config_dir = root / "config"
    output_dir = root / "docs"
    web_dir = root / "web"

    from arxiv_digest.application.digest_service import DigestService

    service = DigestService(config_dir, output_dir, web_dir)

    if args.set_week is not None:
        service.set_week(args.set_week)
        return

    if args.rebuild_web_only:
        service.rebuild_web_only()
        print("Web regenerada en docs/index.html")
        return

    today = datetime.date.today()
    print(f"arXiv Digest — {today.strftime('%d %b %Y')}")
    print("Fetching papers...")

    digest = service.run(
        topics=args.topics,
        days_back=args.days,
        max_per_topic=args.max_per_topic,
        output_dir=output_dir,
    )

    print(f"\nTotal nuevos: {digest.total()} papers")

    if digest.tentative_list:
        print(f"\nLista tentativa ({len(digest.tentative_list)} papers):")
        for t in digest.tentative_list:
            badge = "[ALTA]" if t.priority == "alta" else "[MEDIA]"
            print(f"  {badge} {t.paper.title[:60]}... ({t.paper.topic_label})")

    print(f"\nGuardado en docs/data/{today.isoformat()}.json")
    print("Web regenerada en docs/index.html")


if __name__ == "__main__":
    main()
