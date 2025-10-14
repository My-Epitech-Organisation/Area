##
## EPITECH PROJECT, 2025
## Area
## File description:
## Makefile
##

# =============================================================================
# AREA Project Makefile
# =============================================================================
# Clean, modular Docker Compose commands for dev/prod/test environments
# Documentation: docs/DOCKER_COMPOSE.md
# =============================================================================

.PHONY: help dev prod test \
		up-dev up-prod up-test down-dev down-prod down-test \
		logs-dev logs-prod logs-test restart-dev restart-prod test-shell \
		build shell migrate makemigrations superuser init-db \
		lint format ruff-check ruff-fix \
		status health clean restart \
		db-shell db-dump env validate

# Default target
help: ## Show this help message
	@echo "╔══════════════════════════════════════════════════════════════╗"
	@echo "║              AREA Project - Available Commands               ║"
	@echo "╚══════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make dev       - Start development (hot reload)"
	@echo "  make prod      - Start production (nginx)"
	@echo "  make test      - Run tests (CI-ready)"
	@echo "  make validate  - Validate Docker Compose architecture"
	@echo ""
	@echo "📦 Environment Management:"
	@grep -E '^(up-dev|down-dev|logs-dev|restart-dev|up-prod|down-prod|logs-prod|restart-prod|up-test|down-test|logs-test|test-shell):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🔧 Backend Commands:"
	@grep -E '^(shell|migrate|makemigrations|superuser|init-db):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "✨ Code Quality:"
	@grep -E '^(lint|format|ruff-check|ruff-fix):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🗄️  Database:"
	@grep -E '^(db-shell|db-dump):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🛠️  Utilities:"
	@grep -E '^(build|status|health|clean|restart|env):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "📖 Full documentation: docs/DOCKER_COMPOSE.md"

# =============================================================================
# QUICK START COMMANDS
# =============================================================================

dev: ## Start development (hot reload, Vite on :5173)
	@echo "🚀 Starting AREA in DEVELOPMENT mode..."
	@echo "   Frontend: http://localhost:5173 (Vite hot reload)"
	@echo "   Backend:  http://localhost:8080"
	@echo "   Flower:   http://localhost:5555"
	@docker-compose up -d --remove-orphans
	@echo "✅ Services started! Run 'make logs-dev' to see logs"

prod: ## Start production (nginx on :8081)
	@echo "🚀 Starting AREA in PRODUCTION mode..."
	@echo "   Frontend: http://localhost:8081 (nginx)"
	@echo "   ⚠️  For production servers, use: ./deployment/manage.sh start"
	@echo "📦 Checking for dependency changes..."
	@docker-compose build client_web 2>/dev/null || true
	@docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "✅ Production services started!"

test: ## Run all tests (pytest + tmpfs volumes)
	@echo "🧪 Running tests with optimized test environment..."
	@docker-compose -f docker-compose.yml -f docker-compose.test.yml up --abort-on-container-exit
	@docker-compose -f docker-compose.yml -f docker-compose.test.yml down

validate: ## Validate Docker Compose architecture
	@bash scripts/validate-docker-compose.sh

# =============================================================================
# DEVELOPMENT ENVIRONMENT
# =============================================================================

up-dev: ## Start dev services (detached)
	@docker-compose up -d --remove-orphans

down-dev: ## Stop dev services
	@docker-compose down

logs-dev: ## Show dev logs (follow)
	@docker-compose logs -f

restart-dev: ## Restart dev services
	@docker-compose restart

# =============================================================================
# PRODUCTION ENVIRONMENT
# =============================================================================

up-prod: ## Start prod services (detached)
	@docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

down-prod: ## Stop prod services
	@docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

logs-prod: ## Show prod logs (follow)
	@docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

restart-prod: ## Restart prod services
	@docker-compose -f docker-compose.yml -f docker-compose.prod.yml restart

# =============================================================================
# TEST ENVIRONMENT
# =============================================================================

up-test: ## Start test services (foreground)
	@docker-compose -f docker-compose.yml -f docker-compose.test.yml up --abort-on-container-exit

down-test: ## Stop test services
	@docker-compose -f docker-compose.yml -f docker-compose.test.yml down

logs-test: ## Show test logs
	@docker-compose -f docker-compose.yml -f docker-compose.test.yml logs

test-shell: ## Open bash in test server
	@docker-compose -f docker-compose.yml -f docker-compose.test.yml run --rm server bash

# =============================================================================
# BACKEND COMMANDS
# =============================================================================

shell: ## Open Django shell
	@docker-compose exec server python manage.py shell

migrate: ## Run Django migrations
	@docker-compose exec server python manage.py migrate

makemigrations: ## Create Django migrations
	@docker-compose exec server python manage.py makemigrations

superuser: ## Create Django superuser
	@docker-compose exec server python manage.py createsuperuser

init-db: ## Initialize DB with services/actions/reactions
	@docker-compose exec server python manage.py init_services

init-db-reset: ## Reset and reinitialize DB (⚠️ DELETES ALL DATA)
	@echo "⚠️  WARNING: This will DELETE all services, actions, and reactions!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose exec server python manage.py init_services --reset; \
	else \
		echo "Cancelled."; \
	fi

# =============================================================================
# CODE QUALITY & LINTING
# =============================================================================

lint: ## Run comprehensive linting (Ruff + Bandit)
	@docker-compose exec server bash scripts/lint-check.sh

format: ## Auto-fix formatting and imports (Ruff)
	@docker-compose exec server bash scripts/lint-fix.sh

ruff-check: ## Run Ruff linting only
	@docker-compose exec server ruff check .

ruff-fix: ## Auto-fix Ruff issues
	@docker-compose exec server ruff check --fix .

# =============================================================================
# DATABASE OPERATIONS
# =============================================================================

db-shell: ## Open PostgreSQL shell
	@docker-compose exec db psql -U $$(grep DB_USER .env | cut -d '=' -f2) -d $$(grep DB_NAME .env | cut -d '=' -f2)

db-dump: ## Create database backup
	@echo "📦 Creating database dump..."
	@docker-compose exec -T db pg_dump -U $$(grep DB_USER .env | cut -d '=' -f2) $$(grep DB_NAME .env | cut -d '=' -f2) > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created: backup_$$(date +%Y%m%d_%H%M%S).sql"

# =============================================================================
# UTILITIES
# =============================================================================

build: ## Build all Docker images
	@docker-compose build

rebuild: ## Rebuild Docker images (no cache)
	@echo "🔨 Rebuilding all images without cache..."
	@docker-compose build --no-cache
	@echo "✅ Rebuild complete!"

rebuild-frontend: ## Rebuild frontend only (no cache) - useful after package.json changes
	@echo "🔨 Rebuilding frontend without cache..."
	@docker-compose build --no-cache client_web
	@echo "✅ Frontend rebuild complete!"

rebuild-backend: ## Rebuild backend only (no cache) - useful after requirements.txt changes
	@echo "🔨 Rebuilding backend without cache..."
	@docker-compose build --no-cache server worker beat
	@echo "✅ Backend rebuild complete!"

status: ## Show container status
	@docker-compose ps

health: ## Check backend health
	@curl -f http://localhost:8080/health/ && echo "✅ Backend is healthy" || echo "❌ Backend is not healthy"

clean: ## Clean Docker resources (⚠️ removes volumes)
	@echo "⚠️  WARNING: This will remove all volumes and orphaned containers!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v --remove-orphans; \
		docker system prune -f; \
		echo "✅ Cleanup complete"; \
	else \
		echo "Cancelled."; \
	fi

restart: ## Restart all dev services
	@docker-compose restart

env: ## Copy .env.example to .env
	@if [ -f .env ]; then \
		echo "⚠️  .env already exists. Backup created as .env.backup"; \
		cp .env .env.backup; \
	fi
	@cp .env.example .env
	@echo "✅ .env created from .env.example"
	@echo "📝 Please edit .env with your configuration"