# AREA Backend - Docker Configuration

## 🚀 Quick Start

### Prerequisites

- Docker
- Docker Compose
- Make (optional, for convenience commands)

### Setup

1. **Copy environment file:**

```bash
cp .env.example .env
```

2. **Edit configuration:**
Edit `.env` file with your settings (database passwords, secret keys, etc.)

3. **Build and start services:**

```bash
make build
make up
```

Or without Make:

```bash
docker-compose build
docker-compose up -d
```

4. **Check health:**

```bash
make health
# or
curl http://localhost:8080/health/
```

## 🏗️ Architecture

### Services

- **server**: Django ASGI application with WebSocket support (port 8080)
- **worker**: Celery worker for background tasks
- **beat**: Celery beat scheduler for periodic tasks
- **flower**: Celery monitoring dashboard (port 5555)
- **db**: PostgreSQL database
- **redis**: Redis for Celery broker, caching, and Django Channels

### Key Features

- ✅ ASGI with Gunicorn + UvicornWorker for WebSocket support
- ✅ Django Channels for real-time features
- ✅ Multi-stage Docker build for optimization
- ✅ Health checks for monitoring
- ✅ Automatic database migrations on startup
- ✅ Celery Beat with database scheduler
- ✅ Flower monitoring dashboard
- ✅ Comprehensive logging

## 🛠️ Development

### Common Commands

```bash
# View logs
make logs-backend

# Django shell
make shell

# Run migrations
make migrate

# Create superuser
make superuser

# Run tests
make test

# Code formatting
make format

# Celery monitoring
make flower           # Open Flower dashboard

# Celery management
make celery-status    # Check worker status
make celery-purge     # Clear all tasks
```

### Environment Variables

Key variables in `.env`:

- `DB_USER`, `DB_PASSWORD`, `DB_NAME`: Database config
- `SECRET_KEY`: Django secret key
- `DEBUG`: Enable debug mode
- `BACKEND_PORT`: Backend port (default: 8080)

## 🔍 Monitoring

### Health Endpoints

- `/health/`: Full health check (database, redis)
- `/ready/`: Readiness probe
- `/live/`: Liveness probe

### Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f server

# Worker only
docker-compose logs -f worker
```

## 🐞 Troubleshooting

### Common Issues

1. **Database connection failed:**

   ```bash
   # Check database status
   docker-compose ps db

   # View database logs
   docker-compose logs db
   ```

2. **Redis connection failed:**

   ```bash
   # Check Redis status
   docker-compose ps redis
   ```

3. **Permission errors:**

   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER ./backend
   ```

4. **Port already in use:**

   ```bash
   # Check what's using port 8080
   lsof -i :8080

   # Change port in .env
   FRONTEND_PORT=8082
   ```

### Reset Everything

```bash
make clean
make build
make up
```

## 📦 Production Considerations

For production deployment:

1. **Update .env:**
   - Set `DEBUG=False`
   - Use strong `SECRET_KEY`
   - Configure proper database credentials
   - Set `ALLOWED_HOSTS` appropriately

2. **Security:**
   - Use secrets management
   - Enable HTTPS
   - Configure proper CORS settings
   - Regular security updates

3. **Scaling:**
   - Use docker-compose override files
   - Add load balancer
   - Scale worker services: `docker-compose up --scale worker=3`

## 🔗 API Documentation

Once running, access:

- Admin: <http://localhost:8080/admin/>
- Health: <http://localhost:8080/health/>
- API: <http://localhost:8080/auth/> (auth endpoints)
- Flower: <http://localhost:5555> (Celery monitoring)

## 🧪 Testing

Run the full test suite:

```bash
make test
```

With coverage:

```bash
docker-compose exec server coverage run --source='.' manage.py test
docker-compose exec server coverage report
```
