# API and Scheduler
FROM python:3.10 as builder

RUN pip install poetry

ENV POETRY_VERSION=1.1.8 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PATH="/opt/poetry/bin:$PATH"

WORKDIR /app
COPY poetry.lock pyproject.toml readme.md config.py configuration.ini ./
COPY api ./api
COPY sources ./sources
COPY waveshare_epd ./waveshare_epd
COPY render/pillow/ ./render/pillow
COPY render/__init__.py ./render/__init__.py
COPY fonts ./fonts
RUN poetry install --no-dev --no-interaction



FROM python:3.10-slim-buster  as final
WORKDIR /app



RUN apt-get update && apt-get install -y --no-install-recommends \
    libxcb1 \
    libx11-6 \
    libxext6 \
    libxrandr2 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxi6 \
    libxtst6 \
    libgtk-3-0 \
    libpango1.0-0 \
    libatk1.0-0 \
    libcairo-gobject2 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libgio-cil \
    libglib2.0-0 \
    libasound2 \
    libxrender1 \
    libfreetype6 \
    libfontconfig1 \
    libdbus-glib-1-2 \
    libx11-xcb1 \
    libdbus-1-3 && \
    rm -rf /var/lib/apt/lists/*
COPY --from=builder /app /app
RUN .venv/bin/playwright install firefox


RUN ls -a .venv/bin

EXPOSE 8000




CMD [ ".venv/bin/python", "-m", "api.main" ]