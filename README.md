# arXiv AI Digest

A self-hosted daily digest system that fetches, filters, and publishes AI research papers from arXiv. Every weekday it queries topics aligned to your learning roadmap (agents, RAG, MLOps, fine-tuning, multimodal, etc.), deduplicates and quality-filters results, builds a curated "read today" tentative list based on your current roadmap phase, saves everything as JSON, and regenerates a static SPA served via GitHub Pages — all from a single CLI command or scheduled GitHub Actions workflow.

## Quickstart with Docker

```bash
# 1. Build
docker build -t arxiv-digest .

# 2. Run (fetches today's papers, writes to docs/)
docker run --rm -v $(pwd)/docs:/app/docs -v $(pwd)/config:/app/config arxiv-digest --days 1

# 3. Open docs/index.html in your browser (or serve it)
python -m http.server 8080 --directory docs
```

## Quickstart without Docker

```bash
# Install (Python 3.12+)
pip install -e .

# Fetch papers
arxiv-digest --days 1

# Only rebuild the web SPA
arxiv-digest --rebuild-web-only

# Update current week in the roadmap
arxiv-digest --set-week 8
```

All output goes to `docs/`. Open `docs/index.html` or deploy the `docs/` folder to any static host.

## GitHub Pages setup

1. Push the repo to GitHub.
2. Go to **Settings → Pages** and set the source to the `gh-pages` branch, root `/`.
3. Go to **Settings → Actions → General** and make sure workflows have **Read and write permissions**.
4. Trigger the **Daily arXiv Digest** workflow manually (Actions tab → workflow → Run workflow) to generate the first digest and deploy.
5. Subsequent runs fire automatically Monday–Friday at 13:00 UTC.

Your site will be live at `https://<username>.github.io/<repo>/`.

## Updating the roadmap

Edit `config/roadmap.yaml`:

```yaml
current_phase: "fase_2"   # change phase
current_week: 3            # change week within that phase
```

Or use the CLI shortcut:

```bash
arxiv-digest --set-week 3
```

The prioritizer will immediately start highlighting papers matching the new phase's `priority_topics`.

## Adding a topic

Edit `config/topics.yaml` and add a new entry under `topics:`:

```yaml
topics:
  my_topic:
    label: "My Topic Label"
    query: "keyword1 keyword2 technique OR method"
```

Then reference `my_topic` in any phase's `priority_topics` or `secondary_topics` in `roadmap.yaml`.

## Project structure

```
arxiv-digest/
├── src/arxiv_digest/
│   ├── domain/models.py          # Paper, Topic, Digest, RoadmapPhase dataclasses
│   ├── application/
│   │   ├── fetcher.py            # Thin wrapper over ArxivClient
│   │   ├── filter.py             # Deduplication + quality filter
│   │   ├── prioritizer.py        # Roadmap-aware tentative list builder
│   │   └── digest_service.py     # Orchestrates fetch → filter → prioritize → save
│   ├── infrastructure/
│   │   ├── arxiv_client.py       # arxiv lib wrapper, rate limiting, retry
│   │   └── storage.py            # JSON persistence + HTML regeneration
│   └── cli.py                    # argparse entry point
├── web/index.html                # Complete SPA (no external deps)
├── config/
│   ├── topics.yaml               # Topic definitions and arXiv categories
│   └── roadmap.yaml              # Learning phases and current position
├── docs/                         # Generated output (served by GitHub Pages)
│   ├── index.html                # Copy of web/index.html
│   └── data/
│       ├── index.json            # Global index with all dates
│       └── YYYY-MM-DD.json       # Per-day digest data
├── .github/workflows/
│   ├── daily_digest.yml          # Scheduled fetch + deploy (Mon-Fri 13:00 UTC)
│   └── deploy_web.yml            # Manual web-only redeploy
├── tests/                        # pytest unit tests
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```
