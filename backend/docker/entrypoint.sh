#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting AREA Backend...${NC}"

# Wait for database to be ready
echo -e "${YELLOW}⏳ Waiting for database...${NC}"
while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
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
echo -e "${YELLOW}🔄 Running database migrations...${NC}"
python manage.py migrate --noinput

# Collect static files
echo -e "${YELLOW}📦 Collecting static files...${NC}"
python manage.py collectstatic --noinput --clear

# Create superuser if it doesn't exist
echo -e "${YELLOW}👤 Creating superuser if needed...${NC}"
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@area.com', 'admin123')
    print('✅ Superuser created: admin / admin123')
else:
    print('ℹ️  Superuser already exists')
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