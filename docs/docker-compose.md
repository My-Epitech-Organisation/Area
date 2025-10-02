# Docker Compose Documentation

This `docker-compose.yml` file sets up a PostgreSQL database environment.

## Services

### 1. postgres

- **Image**: `postgres:16`
- **Environment variables**:
  - `DB_USER`: Database username (`myuser`)
  - `DB_PASSWORD`: User password (`secret_password`)
  - `DB_NAME`: Name of the database created at startup (`area_db`)
- **Exposed ports**:
  - `5432:5432` (access PostgreSQL from the host)
- **Volumes**:
  - `pgdata:/var/lib/postgresql/data` (data persistence)

## Volumes

- `pgdata`: Stores PostgreSQL data
- `redis-data`: Stores Redis data
- `apk_shared`: Shared volume for APK files

## Start

To start the environment:

```sh
docker-compose up -d
```

- PostgreSQL access: `localhost:5432`
- Redis access: `localhost:6379`
- Frontend access: [http://localhost:8081](http://localhost:8081)

## Stop

To stop and remove the containers:

```sh
docker-compose down
```

## Notes

- Change the default passwords for production use.
- Data is persisted using Docker volumes.
