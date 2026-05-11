.PHONY: help dev build test clean docker-up docker-down

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev: ## Start development servers
	@echo "Starting Wind Motion development environment..."
	docker compose up -d postgres neo4j redis
	@echo "Waiting for services..."
	@sleep 5
	@echo "Starting backend..."
	cd backend && pip install -r requirements.txt -q && uvicorn main:app --reload --port 8000 &
	@echo "Starting frontend..."
	cd frontend && npm install -q && npm run dev &

dev-backend: ## Start backend only
	cd backend && pip install -r requirements.txt -q && uvicorn main:app --reload --port 8000

dev-frontend: ## Start frontend only
	cd frontend && npm run dev

docker-up: ## Start all services with Docker
	docker compose up -d

docker-down: ## Stop all services
	docker compose down

docker-build: ## Build Docker images
	docker compose build

build: ## Build frontend for production
	cd frontend && npm run build

test: ## Run tests
	cd backend && python -m pytest tests/ -v

test-backend: ## Run backend tests only
	cd backend && python -m pytest tests/ -v

clean: ## Clean build artifacts
	rm -rf frontend/dist frontend/node_modules
	rm -rf backend/__pycache__ backend/**/__pycache__
	find . -name "*.pyc" -delete

db-migrate: ## Run database migrations
	cd backend && python -m alembic upgrade head

db-reset: ## Reset databases (WARNING: destroys data)
	docker compose down -v
	docker compose up -d postgres neo4j redis

logs: ## Show Docker logs
	docker compose logs -f

status: ## Show service status
	docker compose ps

install: ## Install all dependencies
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

.DEFAULT_GOAL := help
