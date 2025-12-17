## Make the base image configurable so users can override if a registry is unreachable.
## Default to the official Python slim image which is broadly available; you can override
## during build with: --build-arg BASE_IMAGE=mcr.microsoft.com/devcontainers/python:0-3.11
ARG BASE_IMAGE=python:3.11-slim-bullseye
FROM ${BASE_IMAGE}

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Install system dependencies (use a simple retry and clean lists)
RUN set -eux; \
    apt-get update || (sleep 1 && apt-get update); \
    apt-get -o Acquire::Retries=3 install -y --no-install-recommends --fix-missing build-essential ca-certificates; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
