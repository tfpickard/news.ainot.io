#!/usr/bin/env bash
f="-f docker-compose.prod.yml"
docker compose $f down; docker compose $f up --build -d; docker compose $f logs -f
