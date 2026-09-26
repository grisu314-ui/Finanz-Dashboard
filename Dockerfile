# syntax=docker/dockerfile:1
# One image for both services (web, worker). Python minor version pinned.
FROM python:3.14-slim-trixie

# Non-root default user. In operation the Dockge stack sets the user from .env
# (compose.dockge.yaml, `user:`; E-29), so the image needs no rebuild for another UID.
ARG UID=1000
ARG GID=1000

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

# Wheels only: the build fails instead of compiling anything on the host.
COPY requirements.txt .
RUN pip install --only-binary=:all: -r requirements.txt

RUN groupadd --gid "${GID}" fever \
 && useradd --uid "${UID}" --gid "${GID}" --no-create-home --home-dir /nonexistent \
            --shell /usr/sbin/nologin fever

COPY alembic.ini ./
COPY migrations/ migrations/
COPY fever/ fever/
COPY config/ config/
RUN python -m compileall -q fever migrations

# No VOLUME instruction on purpose: a forgotten bind mount must fail loudly
# instead of silently writing to an anonymous volume. Data lives in /data (compose).
USER fever
