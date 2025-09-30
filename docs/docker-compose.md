# Docker Compose Documentation

This `docker-compose.yml` file sets up a PostgreSQL database environment with a PgAdmin administration interface.

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

### 2. pgadmin

- **Image**: `dpage/pgadmin4`
- **Environment variables**:
  - `PGADMIN_DEFAULT_EMAIL`: Login email (`admin@example.com`)
  - `PGADMIN_DEFAULT_PASSWORD`: Password (`admin_password`)
- **Exposed ports**:
  - `8080:80` (access PgAdmin via http://localhost:8080)
- **Volumes**:
  - `pgadmin_data:/var/lib/pgadmin` (PgAdmin data persistence)
- **depends_on**:
  - `postgres` (PgAdmin starts after PostgreSQL)

## Volumes

- `pgdata`: Stores PostgreSQL data
- `pgadmin_data`: Stores PgAdmin data

## Start

To start the environment:

```sh
docker-compose up -d
```

- PostgreSQL access: `localhost:5432`
- PgAdmin access: [http://localhost:8080](http://localhost:8080)

## Stop

To stop and remove the containers:

```sh
docker-compose down
```

## Notes

- Change the default passwords for production use.
- Data is persisted using Docker volumes.
