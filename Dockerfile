FROM python:3.12-slim-bookworm

WORKDIR /app

RUN pip install --no-cache-dir poetry
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --only main --no-root
COPY billing/ ./billing/
CMD ["python", "-m", "billing.main"]