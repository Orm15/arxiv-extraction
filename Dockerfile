FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY src/ src/
COPY config/ config/
COPY web/ web/

ENTRYPOINT ["python", "-m", "arxiv_digest"]
