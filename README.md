# Area

This repository contains the Area project - an Action-Reaction automation platform.

**Tech Stack:**
- Backend: Django 5.2.6 + Django REST Framework + Celery
- Frontend: React 19 + Vite 7 + TypeScript + Tailwind CSS
- Mobile: Flutter
- Infrastructure: Docker Compose (8 services)

---

## 🚀 Quick Start

### 1. Environment Setup

All environment variables are centralized in the root `.env` file:

```bash
# Copy the template
cp .env.example .env

# Edit with your values (OAuth credentials, secrets, etc.)
nano .env

# Validate your configuration
./scripts/validate-env.sh
```

**Important Files:**
- `.env` - Your local configuration (gitignored, contains secrets)
- `.env.example` - Template with all required variables documented
- `.env.production` - Production-ready template for deployment
- `scripts/validate-env.sh` - Validation script to check configuration

### 2. Start with Docker Compose

```bash
# Build all services
docker-compose build

# Start all services (development mode with hot-reload)
docker-compose up

# Or start in detached mode
docker-compose up -d
```

**Services will be available at:**
- Frontend (Vite dev): http://localhost:5173
- Backend API: http://localhost:8080
- Flower (Celery monitoring): http://localhost:5566
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### 3. Access the Application

1. Open http://localhost:5173 in your browser
2. Create an account or login
3. Connect services (Google, GitHub, etc.)
4. Create your first automation (Area = Action + Reaction)

---

## 📋 Environment Variables

The project uses a **centralized environment configuration** at the root level. All services (backend, frontend, mobile) read from the same `.env` file.

### Required Variables (44 total)

Variables are organized in 14 categories:
1. **Database** (PostgreSQL): DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT
2. **Redis**: REDIS_PORT, REDIS_URL
3. **Django Backend**: BACKEND_PORT, SECRET_KEY, DEBUG, ENVIRONMENT
4. **Logging**: LOG_LEVEL, DJANGO_LOG_FILE
5. **JWT Authentication**: JWT_SIGNING_KEY
6. **Email (SMTP)**: EMAIL_*, DEFAULT_FROM_EMAIL
7. **Frontend**: FRONTEND_PORT, FRONTEND_URL, VITE_API_BASE
8. **CORS & Security**: ALLOWED_HOSTS, SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE
9. **OAuth2**: GOOGLE_*, GITHUB_*
10. **Webhooks**: *_WEBHOOK_SECRET
11. **Celery**: CELERY_TIMEZONE, CELERY_TASK_ALWAYS_EAGER
12. **Monitoring**: FLOWER_PORT
13. **Docker**: COMPOSE_PROJECT_NAME

See `.env.example` for detailed documentation of each variable.

### Validation

Run the validation script before starting:

```bash
./scripts/validate-env.sh

# Or validate a specific file
./scripts/validate-env.sh .env.production
```

The script checks:
- ✅ All required variables are present
- ⚠️ Warns about placeholder values
- 🔒 Production security checks (DEBUG=False, SSL settings, etc.)

---

## Frontend

Quick start (frontend)

1. Open a terminal and change to the frontend folder:

    ```bash
    cd frontend
    ```

2. Install dependencies:

    ```bash
    npm install
    ```

3. Start the development server:

    ```bash
    npm run dev
    ```

    The app will be available at http://localhost:5173/ by default.

4. Build for production:

    ```bash
    npm run build
    ```

5. Preview the production build locally:

    ```bash
    npm run preview
    ```

---

## 🐳 Docker Architecture

The project uses Docker Compose with 8 services:

1. **db** - PostgreSQL 16 database
2. **redis** - Redis for Celery task queue
3. **server** - Django backend API (port 8080)
4. **worker** - Celery worker for async tasks
5. **beat** - Celery Beat scheduler for periodic tasks
6. **flower** - Celery monitoring UI (port 5566)
7. **client_mobile** - Flutter mobile app builder
8. **client_web** - React frontend (Vite dev server on port 5173)

### Configuration Files

- `docker-compose.yml` - Base configuration (production-ready)
- `docker-compose.override.yml` - Development overrides (auto-loaded)
- `docker-compose.prod.yml` - Production-specific settings
- `docker-compose.test.yml` - Testing configuration

### Port Mapping (External → Internal)

Docker Compose maps **external host ports** to **internal container ports**. This allows multiple services to use standard ports internally while exposing unique ports on your host machine.

**Format:** `${EXTERNAL_PORT}:internal_port`

| Service | External (Host) | Internal (Container) | Environment Variable | Description |
|---------|-----------------|----------------------|---------------------|-------------|
| **PostgreSQL** | 5433 | 5432 | `DB_PORT=5433` | Database server (standard PostgreSQL port 5432 inside container) |
| **Redis** | 6379 | 6379 | `REDIS_PORT=6379` | Cache & Celery broker (same port, configurable for conflicts) |
| **Django Backend** | 8080 | 8080 | `BACKEND_PORT=8080` | REST API server |
| **Flower** | 5566 | 5555 | `FLOWER_PORT=5566` | Celery monitoring UI (internal Flower default is 5555) |
| **Frontend (Vite)** | 5173 | 5173 | `FRONTEND_PORT=5173` | React development server |

**Why different ports?**

- **Avoid conflicts:** If you already have PostgreSQL running on port 5432 locally, Docker maps to 5433 instead
- **Flexibility:** Change external ports in `.env` without modifying Dockerfiles or container configurations
- **Security:** In production, internal ports are isolated; only exposed ports are accessible from outside

**Example Connection Strings:**

```bash
# From your host machine (e.g., DBeaver, psql)
postgresql://area_user:area_password@localhost:5433/area_db

# From inside Docker containers (e.g., Django backend)
postgresql://area_user:area_password@db:5432/area_db
# Note: Uses service name 'db' and internal port 5432
```

**Configuration in `.env`:**

```bash
# External ports (accessible from host)
DB_PORT=5433              # PostgreSQL external port
REDIS_PORT=6379           # Redis external port
BACKEND_PORT=8080         # Django API external port
FLOWER_PORT=5566          # Flower UI external port
FRONTEND_PORT=5173        # Vite dev server external port

# Internal connection strings (used by containers)
DB_HOST=db                # Docker service name, not 'localhost'
REDIS_HOST=redis          # Docker service name
```

---

## 📚 Additional Documentation

- `HOWTOCONTRIBUTE.md` - Development guidelines and OAuth2 integration guide
- `docs/OAUTH2_IMPLEMENTATION.md` - Comprehensive OAuth2 Backend-First flow documentation
- `docs/docker-compose.md` - Docker Compose detailed documentation
- `backend/README.md` - Backend API documentation

---

Notes

- All environment variables are centralized in the root `.env` file
- Frontend and backend share the same .env through Docker Compose
- If you remove or change dev dependencies in `package.json`, run `npm install` again to update `node_modules`.
- Use `./scripts/validate-env.sh` before deploying to catch configuration errors
