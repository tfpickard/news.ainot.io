.PHONY: help build up down logs test clean

help:
	@echo "Singl News - Available commands:"
	@echo "  make build    - Build all Docker containers"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View logs from all services"
	@echo "  make test     - Run all tests"
	@echo "  make clean    - Remove containers, volumes, and cached files"
	@echo ""
	@echo "Development commands:"
	@echo "  make dev-backend   - Run backend in development mode"
	@echo "  make dev-frontend  - Run frontend in development mode"
	@echo "  make test-backend  - Run backend tests"
	@echo "  make test-frontend - Run frontend tests"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose restart

test: test-backend test-frontend

test-backend:
	cd backend && pytest -v

test-frontend:
	cd frontend && pnpm run test

dev-backend:
	cd backend && python -m app.main

dev-frontend:
	cd frontend && pnpm run dev

clean:
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf backend/.pytest_cache
	rm -rf frontend/node_modules
	rm -rf frontend/.svelte-kit
	rm -rf frontend/build
	rm -rf frontend/.pnpm-store

migrate:
	docker-compose exec backend alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " msg; \
	docker-compose exec backend alembic revision --autogenerate -m "$$msg"

db-shell:
	docker-compose exec db psql -U singl -d singl

backend-shell:
	docker-compose exec backend /bin/bash

frontend-shell:
	docker-compose exec frontend /bin/sh

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && pnpm install
