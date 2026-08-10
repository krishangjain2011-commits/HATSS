FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN groupadd --system hatss \
    && useradd --system --gid hatss --create-home hatss

COPY pyproject.toml ./
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

RUN python -m pip install --upgrade pip \
    && python -m pip install .

RUN chown -R hatss:hatss /app

USER hatss

EXPOSE 8000

FROM base AS development

USER root
RUN python -m pip install ".[dev]"
USER hatss

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS production

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
