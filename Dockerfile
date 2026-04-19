FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/
COPY config/ config/
COPY web/ web/

RUN pip install --no-cache-dir .

ENTRYPOINT ["python", "-m", "arxiv_digest"]
