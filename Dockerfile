FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/
COPY config/ config/
COPY web/ web/

RUN pip install --no-cache-dir . && python -c "import arxiv_digest"

ENV PYTHONPATH=/app/src

ENTRYPOINT ["python", "-m", "arxiv_digest"]
