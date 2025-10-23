#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting AREA Backend...${NC}"

# Fix permissions for mounted volumes in development
if [ -f "/app/manage.py" ]; then
    chmod +x /app/manage.py 2>/dev/null || true
fi

# Ensure log directory exists and is writable
mkdir -p /app/logs
touch /app/logs/django.log
chmod 666 /app/logs/django.log 2>/dev/null || true
chmod 777 /app/logs 2>/dev/null || true

# Wait for database to be ready
echo -e "${YELLOW}⏳ Waiting for database...${NC}"
DB_HOST=${DB_HOST:-db}
while ! nc -z $DB_HOST 5432; do
  echo "Database is unavailable - sleeping"
  sleep 1
done
echo -e "${GREEN}✅ Database is ready!${NC}"

# Wait for Redis to be ready
echo -e "${YELLOW}⏳ Waiting for Redis...${NC}"
while ! nc -z redis ${REDIS_PORT:-6379}; do
  echo "Redis is unavailable - sleeping"
  sleep 1
done
echo -e "${GREEN}✅ Redis is ready!${NC}"

# Run database migrations
echo -e "${YELLOW}🔄 Making migrations...${NC}"
python manage.py makemigrations --noinput

echo -e "${YELLOW}🔄 Running database migrations...${NC}"
python manage.py migrate --noinput

# Collect static files
echo -e "${YELLOW}📦 Collecting static files...${NC}"
python manage.py collectstatic --noinput --clear

# Initialize services (Actions & Reactions)
echo -e "${YELLOW}🔧 Initializing services database...${NC}"
python manage.py init_services
echo -e "${GREEN}✅ Services initialized!${NC}"

# Initialize Celery Beat periodic tasks
echo -e "${YELLOW}⏰ Initializing Celery Beat tasks...${NC}"
python manage.py init_celery_beat
echo -e "${GREEN}✅ Celery Beat tasks initialized!${NC}"

# Create superuser if it doesn't exist
echo -e "${YELLOW}👤 Creating superuser if needed...${NC}"
ADMIN_EMAIL="${DJANGO_SUPERUSER_EMAIL:-admin@areaction.app}"
ADMIN_PASSWORD="${DJANGO_SUPERUSER_PASSWORD:-admin123}"

python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='$ADMIN_EMAIL').exists():
    User.objects.create_superuser(email='$ADMIN_EMAIL', password='$ADMIN_PASSWORD')
    print('✅ Superuser created: $ADMIN_EMAIL')
else:
    print('ℹ️  Superuser already exists: $ADMIN_EMAIL')
EOF

# Load initial data if needed
if [ -f "fixtures/initial_data.json" ]; then
    echo -e "${YELLOW}📊 Loading initial data...${NC}"
    python manage.py loaddata fixtures/initial_data.json
fi

echo -e "${GREEN}🎉 Backend initialization completed!${NC}"
echo -e "${GREEN}📍 Starting server on port 8080...${NC}"

# Execute the main container command
exec "$@"