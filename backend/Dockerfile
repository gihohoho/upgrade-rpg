# syntax=docker/dockerfile:1
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY backend/pyproject.toml /app/pyproject.toml
COPY backend/app /app/app
COPY backend/alembic.ini /app/alembic.ini
COPY backend/alembic /app/alembic

RUN python -m pip install --upgrade pip \
    && python -m pip install .

USER app
EXPOSE 8000

# Migration은 서버 시작과 분리합니다. 이 command에는 Alembic을 묶지 않습니다.
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
