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

build-fast: ## Build only essential services (excludes mobile)
	docker-compose build server client_web

up: ## Start all services
	docker-compose up -d

up-fast: ## Start backend services only (no web/mobile - fastest startup)
	docker-compose up -d db redis server worker beat flower

up-web: ## Start all services except mobile (but includes web - mobile will build)
	docker-compose up -d db redis server worker beat flower client_web

up-logs: ## Start all services with logs
	docker-compose up

up-fast-logs: ## Start all services except mobile with logs (faster startup)
	docker-compose up db redis server worker beat flower client_web

up-mobile: ## Start mobile build service only
	docker-compose up -d client_mobile

up-web-logs: ## Start all services except mobile with logs (but mobile will build)
	docker-compose up db redis server worker beat flower client_web

up-backend-logs: ## Start backend services only with logs (fastest)
	docker-compose up db redis server worker beat flower

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

init-db: ## Initialize database with default services/actions/reactions
	docker-compose exec server python manage.py init_services

init-db-reset: ## Reset and reinitialize database (WARNING: deletes all services)
	docker-compose exec server python manage.py init_services --reset

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

# Code Quality & Linting (using Ruff + custom scripts)
lint: ## Run comprehensive linting check using Ruff-powered scripts
	docker-compose exec server bash scripts/lint-check.sh

lint-check: ## Alias for lint command
	docker-compose exec server bash scripts/lint-check.sh

format: ## Auto-fix code formatting using Ruff-powered scripts
	docker-compose exec server bash scripts/lint-fix.sh

lint-fix: ## Alias for format command
	docker-compose exec server bash scripts/lint-fix.sh

# Individual Ruff commands (for specific checks)
ruff-check: ## Run only Ruff linting checks
	docker-compose exec server ruff check .

ruff-format: ## Check code formatting with Ruff (no changes)
	docker-compose exec server ruff format --check .

ruff-fix: ## Auto-fix all issues with Ruff
	docker-compose exec server ruff check --fix .

ruff-format-fix: ## Fix code formatting with Ruff
	docker-compose exec server ruff format .

# Legacy tools (kept for compatibility - consider using ruff-* commands)
bandit: ## Run security checks with bandit
	docker-compose exec server bandit -r . -x "*/tests/*,*/migrations/*,*/venv/*"

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
	@echo "⚡ Ruff-Powered Code Quality Scripts"
	@echo "=================================="
	@echo "🚀 Performance: 10-100x faster than Black+flake8+isort!"
	@echo ""
	@echo "Available scripts:"
	@echo "  • backend/scripts/lint-check.sh - Comprehensive verification (Ruff + Bandit)"
	@echo "  • backend/scripts/lint-fix.sh   - Auto-fix with Ruff formatter"
	@echo ""
	@echo "Main commands:"
	@echo "  make lint        - Run all checks (~0.6s vs 19s before!)"
	@echo "  make format      - Auto-fix formatting/imports/style"
	@echo "  make ruff-check  - Direct Ruff linting only"
	@echo "  make ruff-fix    - Direct Ruff auto-fixes"
	@echo "  make install-dev - Install dev dependencies"
	@echo ""
	@echo "📊 Tools replaced by Ruff:"
	@echo "  ❌ Black (formatting) → ✅ Ruff format"
	@echo "  ❌ isort (imports) → ✅ Ruff I rules"
	@echo "  ❌ flake8 + plugins → ✅ Ruff linting"
	@echo "  ✅ Bandit (security) - kept for advanced checks"
	@echo ""
	docker-compose exec server pip install -r requirements-dev.txt