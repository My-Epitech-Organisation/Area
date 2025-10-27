#!/bin/bash
###############################################################################
# AREA Production Management Script
# Gestion simplifiée du déploiement en production
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Paths configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Check if running as areaction user (recommended for security)
CURRENT_USER=$(whoami)
if [ "$CURRENT_USER" != "areaction" ] && [ "$CURRENT_USER" != "root" ]; then
    echo -e "${YELLOW}Warning: Running as user '$CURRENT_USER'${NC}"
    echo -e "${YELLOW}Recommended: Run as 'areaction' user for security isolation${NC}"
    echo -e "${YELLOW}Switch with: sudo su - areaction${NC}"
    echo ""
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if .env exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "${RED}Error: .env file not found at $PROJECT_DIR/.env${NC}"
    echo "Run setup.sh first or create .env manually"
    exit 1
fi

# Change to project directory for all docker-compose commands
cd "$PROJECT_DIR" || exit 1

# Help function
show_help() {
    echo "AREA Production Management"
    echo ""
    echo "Usage: ./manage.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start          Start all services"
    echo "  stop           Stop all services"
    echo "  restart        Restart all services"
    echo "  pull           Pull latest code and restart"
    echo "  logs           Show logs (all services)"
    echo "  logs-backend   Show backend logs only"
    echo "  logs-worker    Show worker logs only"
    echo "  logs-beat      Show beat scheduler logs"
    echo "  status         Show status of all containers"
    echo "  reset          Stop, remove containers, volumes and restart"
    echo "  delete         Delete all containers and volumes (DANGER)"
    echo "  backup-db      Backup PostgreSQL database"
    echo "  restore-db     Restore PostgreSQL database"
    echo "  shell          Open Django shell"
    echo "  init-db        Initialize database with services"
    echo "  migrate        Run Django migrations"
    echo "  superuser      Create Django superuser"
    echo "  update         Update to latest version (pull + migrate + restart)"
    echo ""
}

# Start services
start_services() {
    echo -e "${GREEN}Starting AREA services...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    echo -e "${GREEN}Services started${NC}"
    echo ""
    docker-compose ps
}

# Stop services
stop_services() {
    echo -e "${YELLOW}Stopping AREA services...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
    echo -e "${GREEN}Services stopped${NC}"
}

# Restart services
restart_services() {
    echo -e "${YELLOW}Restarting AREA services (down + up to reload .env)...${NC}"

    # Stop and remove containers
    echo -e "${BLUE}→ Stopping containers...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

    # Start containers (will reload .env)
    echo -e "${BLUE}→ Starting containers with fresh .env...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

    echo -e "${GREEN}Services restarted (environment variables reloaded)${NC}"
    echo ""
    docker-compose ps
}

# Pull latest code
pull_update() {
    echo -e "${BLUE}Pulling latest code...${NC}"

    # Stash local changes if any
    if ! git diff-index --quiet HEAD --; then
        echo -e "${YELLOW}Stashing local changes...${NC}"
        git stash
    fi

    # Pull
    git pull origin main

    echo -e "${GREEN}Code updated${NC}"
    echo ""
    echo -e "${YELLOW}Rebuilding containers...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

    echo ""
    echo -e "${YELLOW}Restarting services...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

    echo -e "${GREEN}Update complete${NC}"
}

# Show logs
show_logs() {
    if [ "$1" == "backend" ]; then
        docker-compose logs -f server
    elif [ "$1" == "worker" ]; then
        docker-compose logs -f worker
    elif [ "$1" == "beat" ]; then
        docker-compose logs -f beat
    else
        docker-compose logs -f
    fi
}

# Show status
show_status() {
    echo -e "${BLUE}Service Status:${NC}"
    docker-compose ps
    echo ""
    echo -e "${BLUE}Disk Usage:${NC}"
    docker system df
}

# Reset (delete and restart)
reset_services() {
    echo -e "${RED}WARNING: This will delete all containers and volumes!${NC}"
    read -p "Are you sure? (yes/no): " CONFIRM

    if [ "$CONFIRM" != "yes" ]; then
        echo "Cancelled"
        exit 0
    fi

    echo -e "${YELLOW}Stopping services...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml down -v

    echo -e "${YELLOW}Rebuilding...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

    echo -e "${YELLOW}Starting services...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

    echo -e "${YELLOW}Waiting for database...${NC}"
    sleep 10

    echo -e "${YELLOW}Running migrations...${NC}"
    docker-compose exec server python manage.py migrate

    echo -e "${YELLOW}Initializing database...${NC}"
    docker-compose exec server python manage.py init_services

    echo -e "${GREEN}Reset complete${NC}"
}

# Delete everything
delete_all() {
    echo -e "${RED}⚠️  DANGER: This will DELETE ALL containers, volumes, and data!${NC}"
    echo -e "${RED}This action cannot be undone!${NC}"
    echo ""
    read -p "Type 'DELETE' to confirm: " CONFIRM

    if [ "$CONFIRM" != "DELETE" ]; then
        echo "Cancelled"
        exit 0
    fi

    echo -e "${RED}Deleting everything...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml down -v --remove-orphans

    # Remove images
    echo -e "${YELLOW}Removing images...${NC}"
    docker images | grep area | awk '{print $3}' | xargs -r docker rmi -f

    echo -e "${GREEN}All containers and volumes deleted${NC}"
}

# Backup database
backup_database() {
    BACKUP_DIR="backups"
    mkdir -p $BACKUP_DIR

    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/area_backup_$TIMESTAMP.sql"

    echo -e "${BLUE}Backing up database...${NC}"

    # Check if db container is running
    if ! docker-compose ps db | grep -q "Up"; then
        echo -e "${YELLOW}Warning: Database container not running, skipping backup${NC}"
        return 0
    fi

    # Try backup with error handling
    if docker-compose exec -T db pg_dump -U area_user area_db > "$BACKUP_FILE" 2>/dev/null; then
        # Compress
        gzip "$BACKUP_FILE"
        echo -e "${GREEN}Backup saved: ${BACKUP_FILE}.gz${NC}"

        # Keep only last 10 backups
        ls -t "$BACKUP_DIR"/*.gz 2>/dev/null | tail -n +11 | xargs -r rm
        echo "Old backups cleaned (keeping last 10)"
    else
        echo -e "${YELLOW}Warning: Backup failed, but continuing with update${NC}"
        rm -f "$BACKUP_FILE" 2>/dev/null
    fi
}

# Restore database
restore_database() {
    BACKUP_DIR="backups"

    if [ ! -d "$BACKUP_DIR" ]; then
        echo -e "${RED}No backups found${NC}"
        exit 1
    fi

    echo -e "${BLUE}Available backups:${NC}"
    ls -lh $BACKUP_DIR/*.gz
    echo ""

    read -p "Enter backup filename: " BACKUP_FILE

    if [ ! -f "$BACKUP_DIR/$BACKUP_FILE" ]; then
        echo -e "${RED}Backup file not found${NC}"
        exit 1
    fi

    echo -e "${YELLOW}Restoring database...${NC}"
    gunzip -c $BACKUP_DIR/$BACKUP_FILE | docker-compose exec -T db psql -U area_user area_db

    echo -e "${GREEN}Database restored${NC}"
}

# Django shell
django_shell() {
    docker-compose exec server python manage.py shell
}

# Initialize database
init_database() {
    echo -e "${BLUE}Initializing database with services...${NC}"
    docker-compose exec server python manage.py init_services
    echo -e "${GREEN}Database initialized${NC}"
}

# Run migrations
run_migrations() {
    echo -e "${BLUE}Running migrations...${NC}"
    docker-compose exec server python manage.py migrate
    echo -e "${GREEN}Migrations complete${NC}"
}

# Create superuser
create_superuser() {
    echo -e "${BLUE}Creating Django superuser...${NC}"
    docker-compose exec server python manage.py createsuperuser
}

# Full update (pull + migrate + restart)
full_update() {
    echo -e "${BLUE}Running full update...${NC}"

    # Backup database first
    echo -e "${YELLOW}Creating backup before update...${NC}"
    backup_database

    # Detect current branch
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo -e "${BLUE}Current branch: ${CURRENT_BRANCH}${NC}"

    # Pull code from current branch
    echo -e "${YELLOW}Pulling latest code from ${CURRENT_BRANCH}...${NC}"
    git pull origin "$CURRENT_BRANCH"

    # Show what changed
    echo -e "${BLUE}Recent changes:${NC}"
    git log -3 --oneline

    # Rebuild with no-cache for frontend and backend to ensure all code changes are applied
    echo -e "${YELLOW}Rebuilding containers (no-cache for frontend and backend)...${NC}"
    echo -e "${BLUE}→ Building client_web (React/Vite with VITE_API_BASE=${VITE_API_BASE})...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache client_web
    echo -e "${BLUE}→ Building server (Django)...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache server
    echo -e "${BLUE}→ Building worker and beat...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml build worker beat

    # Stop services
    echo -e "${YELLOW}Stopping services...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

    # Start services
    echo -e "${YELLOW}Starting services...${NC}"
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

    # Wait for DB
    sleep 10

    # Run migrations
    echo -e "${YELLOW}Running migrations...${NC}"
    docker-compose exec server python manage.py migrate

    # Collect static
    echo -e "${YELLOW}Collecting static files...${NC}"
    docker-compose exec server python manage.py collectstatic --noinput

    # Healthcheck
    echo ""
    echo -e "${YELLOW}Running healthcheck...${NC}"
    sleep 15  # Wait for services to fully start

    HEALTHCHECK_PASSED=false
    for i in {1..10}; do
        if docker-compose exec -T server curl -f http://localhost:8080/health/ > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Health check passed!${NC}"
            HEALTHCHECK_PASSED=true
            break
        fi
        echo -e "${BLUE}⏳ Attempt $i/10 - waiting for services...${NC}"
        sleep 5
    done

    if [ "$HEALTHCHECK_PASSED" = false ]; then
        echo -e "${RED}❌ Health check failed after 10 attempts!${NC}"
        echo -e "${RED}Services may not be healthy. Check logs with: ./manage.sh logs${NC}"
        echo ""
        echo -e "${YELLOW}Container status:${NC}"
        docker-compose ps
        exit 1
    fi

    echo ""
    echo -e "${GREEN}✅ Update complete and services are healthy!${NC}"
    echo ""
    docker-compose ps
}

# Main script
case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    pull)
        pull_update
        ;;
    logs)
        show_logs
        ;;
    logs-backend)
        show_logs backend
        ;;
    logs-worker)
        show_logs worker
        ;;
    logs-beat)
        show_logs beat
        ;;
    status)
        show_status
        ;;
    reset)
        reset_services
        ;;
    delete)
        delete_all
        ;;
    backup-db)
        backup_database
        ;;
    restore-db)
        restore_database
        ;;
    shell)
        django_shell
        ;;
    init-db)
        init_database
        ;;
    migrate)
        run_migrations
        ;;
    superuser)
        create_superuser
        ;;
    update)
        full_update
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
