# Area

## Overview

This is a proof-of-concept (POC) full-stack application demonstrating a microservices architecture with multiple clients. It includes a backend server, a job worker, web and mobile clients, all orchestrated via Docker Compose.

## Architecture

The application consists of the following components:

- **Database**: PostgreSQL for data persistence
- **Cache/Queue**: Redis for caching and job queuing
- **Server**: Node.js/TypeScript API server using Fastify
- **Worker**: Node.js/TypeScript job processor using BullMQ
- **Client Web**: React/TypeScript web application
- **Client Mobile**: Flutter/Dart mobile application

## Components

### Database (db)
- **Technology**: PostgreSQL 15
- **Purpose**: Stores application data
- **Port**: 5432

### Cache/Queue (redis)
- **Technology**: Redis 7
- **Purpose**: Caching and job queue management
- **Port**: 6379

### Server
- **Technology**: Node.js with TypeScript
- **Framework**: Express.js
- **Dependencies**: BullMQ, ioredis, pg
- **Purpose**: Provides REST API endpoints
- **Port**: 8080
- **Endpoints**:
  - `GET /about.json`: Returns server information
  - `GET /ping-redis`: Tests Redis connection
  - `GET /test-db`: Tests database connection
  - `POST /enqueue`: Adds job to queue
  - `GET /users`: Get all users
  - `GET /users/:id`: Get user by ID
  - `POST /users`: Create new user
  - `PUT /users/:id`: Update user
  - `DELETE /users/:id`: Delete user

### Worker
- **Technology**: Node.js with TypeScript
- **Dependencies**: BullMQ, ioredis
- **Purpose**: Processes background jobs from the queue

### Client Web
- **Technology**: React with TypeScript
- **Purpose**: Web interface for user management (list, add, delete users) and APK download
- **Port**: 8081 (nginx)
- **Features**:
  - User listing with real-time updates
  - Add new users
  - Delete existing users
  - Download mobile APK

### Client Mobile
- **Technology**: Flutter with Dart
- **Purpose**: Mobile application for user management
- **Dependencies**: http package
- **Platforms**: Android, iOS, Linux, macOS, Windows, Web
- **Features**:
  - User listing
  - Add new users
  - Delete users
  - Real-time API integration

### Shared Volume
- **Purpose**: Shared storage between containers
- **Contents**: Mobile APK file

## Prerequisites

- Docker and Docker Compose
- For local development: Node.js, Flutter SDK, React development tools

## Quick Start

1. Clone the repository
2. Navigate to the `Poc/complet` directory
3. Run `docker-compose up --build`

This will start all services and make them available on their respective ports.

## Development

### Server
```bash
cd Poc/complet/server
npm install
npm run dev  # Runs with ts-node-dev
npm run build  # Compiles TypeScript
```

### Worker
```bash
cd Poc/complet/worker
npm install
npm run dev
npm run build
```

### Client Web
```bash
cd Poc/complet/client_web
npm install
npm start  # Development server
npm run build  # Production build
```

### Client Mobile
```bash
cd Poc/complet/client_mobile
flutter pub get
flutter run  # Runs on connected device/emulator
flutter build apk  # Builds Android APK
```

## Environment Variables

### Server
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection URL

### Worker
- `REDIS_URL`: Redis connection URL
- `TEST_MODE`: Set to "true" to enable test job generation

## Docker

Each component has its own Dockerfile for containerization. The `docker-compose.yml` orchestrates the entire stack.

## API Documentation

### User Management API

The application provides a complete CRUD API for user management:

#### Get All Users
```
GET /users
```
**Response**: Array of user objects

#### Get User by ID
```
GET /users/:id
```
**Parameters**: `id` (integer) - User ID
**Response**: User object or 404 if not found

#### Create User
```
POST /users
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com"
}
```
**Response**: Created user object (201) or error (400/409)

#### Update User
```
PUT /users/:id
Content-Type: application/json

{
  "name": "Jane Doe",
  "email": "jane@example.com"
}
```
**Parameters**: `id` (integer) - User ID
**Response**: Updated user object or 404 if not found

#### Delete User
```
DELETE /users/:id
```
**Parameters**: `id` (integer) - User ID
**Response**: Success message or 404 if not found

### User Object Schema
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "created_at": "2025-01-22T10:30:00.000Z"
}
```

## Local Access URLs

Once all services are running with `docker-compose up`, you can access the application through these URLs:

- **Web Client**: http://localhost:8081
  - Main web interface
  - Displays server information from `/about.json`
  - Provides download link for mobile APK

- **API Server**: http://localhost:8080
  - REST API endpoints
  - Example: `GET http://localhost:8080/about.json`

- **Database**: localhost:5432
  - PostgreSQL database
  - User: area, Password: area, Database: area
  - Can be accessed with PostgreSQL client tools

- **Redis**: localhost:6379
  - Redis cache and queue
  - Can be accessed with Redis CLI tools

## Notes

- This is a proof-of-concept implementation
- The mobile app is built as a Flutter application supporting multiple platforms
- The web client serves the mobile APK for download
- Job processing is handled asynchronously via BullMQ