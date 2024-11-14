FROM python:3.12-slim as builder
# Install dependencies with apt (for Debian-based images)
RUN apt-get update && apt-get install -y gcc musl-dev libffi-dev openssl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir --upgrade pip poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \ 
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN poetry install --no-interaction --no-dev --no-ansi && rm -rf $POETRY_CACHE_DIR

FROM python:3.12-slim as production
# Install chromium and chromedriver dependencies using apt
RUN apt-get update && apt-get install -y chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get upgrade -y

ENV PYTHONPATH=/app/src
ENV UVICORN_PATH=/usr/local/bin/uvicorn
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

RUN addgroup --system www && adduser --system appuser --ingroup www

COPY --from=builder  ${VIRTUAL_ENV} ${VIRTUAL_ENV}
WORKDIR /app
COPY . .

RUN chgrp -R www ${VIRTUAL_ENV} /app && chmod -R u+rx ${VIRTUAL_ENV} /app

USER appuser
EXPOSE 8000
CMD ["uvicorn", "web_pilot.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
