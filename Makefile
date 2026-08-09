.PHONY: help dev-up dev-down lint test migrate seed-secrets eval

help:
	@echo "EKBA Development Commands:"
	@echo "  make dev-up      - Spin up local infrastructure (Qdrant, Redis, Postgres, LocalStack)"
	@echo "  make dev-down    - Tear down local infrastructure"
	@echo "  make lint        - Run ruff, black, and mypy type checks"
	@echo "  make test        - Run pytest suite (unit, security, agent)"
	@echo "  make migrate     - Run database migrations via Alembic"
	@echo "  make api         - Start FastAPI backend server"
	@echo "  make frontend    - Start Vite frontend dev server"

dev-up:
	docker compose -f docker-compose.dev.yml up -d

dev-down:
	docker compose -f docker-compose.dev.yml down

lint:
	ruff check backend/app
	black --check backend/app
	mypy backend/app

test:
	pytest backend/tests

migrate:
	cd backend && alembic upgrade head

api:
	cd backend && .venv/Scripts/python -m uvicorn app.main:app --port 8000 --reload

frontend:
	cd frontend && npm run dev

eval:
	python backend/evals/run_eval.py
