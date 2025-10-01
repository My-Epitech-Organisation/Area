# AREA Project Makefile
# Simplified Docker operations

.PHONY: help build up down logs shell migrate test lint clean status

# Default target
help: ## Show this help message
	@echo "AREA Project - Available commands:"
	@echo
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Docker operations
build: ## Build all Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

up-logs: ## Start all services with logs
	docker-compose up

down: ## Stop all services
	docker-compose down

down-v: ## Stop all services and remove volumes
	docker-compose down -v

logs: ## Show logs for all services
	docker-compose logs -f

logs-backend: ## Show backend logs only
	docker-compose logs -f server

# Backend specific commands
shell: ## Open Django shell in backend container
	docker-compose exec server python manage.py shell

migrate: ## Run Django migrations
	docker-compose exec server python manage.py migrate

makemigrations: ## Create new Django migrations
	docker-compose exec server python manage.py makemigrations

superuser: ## Create Django superuser
	docker-compose exec server python manage.py createsuperuser

# Celery commands
celery-status: ## Check Celery worker status
	docker-compose exec worker celery -A area_project status

celery-purge: ## Purge all Celery tasks
	docker-compose exec worker celery -A area_project purge -f

flower: ## Open Flower monitoring interface
	@echo "Opening Flower at http://localhost:5555"
	@open http://localhost:5555 2>/dev/null || xdg-open http://localhost:5555 2>/dev/null || echo "Please open http://localhost:5555 manually"

# Testing and development
test: ## Run Django tests
	docker-compose exec server python manage.py test

# Code Quality & Linting (using custom scripts)
lint: ## Run comprehensive linting check using custom scripts
	docker-compose exec server bash scripts/lint-check.sh

lint-check: ## Alias for lint command
	docker-compose exec server bash scripts/lint-check.sh

format: ## Auto-fix code formatting using custom scripts
	docker-compose exec server bash scripts/lint-fix.sh

lint-fix: ## Alias for format command
	docker-compose exec server bash scripts/lint-fix.sh

# Individual linting tools (for specific checks)
flake8: ## Run only flake8 checks
	docker-compose exec server flake8 .

black-check: ## Check code formatting with black (no changes)
	docker-compose exec server black --check .

black-fix: ## Fix code formatting with black
	docker-compose exec server black .

isort-check: ## Check import sorting with isort (no changes)
	docker-compose exec server isort --check-only .

isort-fix: ## Fix import sorting with isort
	docker-compose exec server isort .

# Monitoring
status: ## Show status of all containers
	docker-compose ps

health: ## Check health of backend service
	curl -f http://localhost:8080/health/ || echo "Backend is not healthy"

logs-worker: ## Show Celery worker logs
	docker-compose logs -f worker

logs-beat: ## Show Celery beat logs
	docker-compose logs -f beat

logs-flower: ## Show Flower logs
	docker-compose logs -f flower

# Cleanup
clean: ## Clean up Docker resources
	docker-compose down -v --remove-orphans
	docker system prune -f

restart: ## Restart all services
	docker-compose restart

restart-backend: ## Restart only backend service
	docker-compose restart server

# Database operations
db-shell: ## Open PostgreSQL shell
	docker-compose exec db psql -U $(shell grep DB_USER .env | cut -d '=' -f2) -d $(shell grep DB_NAME .env | cut -d '=' -f2)

db-dump: ## Create database dump
	docker-compose exec db pg_dump -U $(shell grep DB_USER .env | cut -d '=' -f2) $(shell grep DB_NAME .env | cut -d '=' -f2) > backup.sql

# Environment setup
env: ## Copy .env.example to .env
	cp .env.example .env
	@echo "Please edit .env file with your configuration"

install-dev: ## Install development dependencies in backend container
	docker-compose exec server pip install -r requirements-dev.txt

# Code quality helpers
lint-install: ## Install linting dependencies and show script info
	@echo "📋 Code Quality Scripts Information"
	@echo "=================================="
	@echo "Available scripts:"
	@echo "  • backend/scripts/lint-check.sh - Comprehensive code verification"
	@echo "  • backend/scripts/lint-fix.sh   - Auto-fix code formatting"
	@echo ""
	@echo "Main commands:"
	@echo "  make lint        - Run all checks (recommended)"
	@echo "  make format      - Auto-fix formatting issues"
	@echo "  make install-dev - Install dev dependencies"
	@echo ""
	docker-compose exec server pip install -r requirements-dev.txt