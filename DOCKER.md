# 🐳 Docker Documentation - Fleet Management System

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Docker Configuration](#docker-configuration)
- [Environment Variables](#environment-variables)
- [Container Architecture](#container-architecture)
- [Docker Commands](#docker-commands)
- [Troubleshooting](#troubleshooting)
- [Production Deployment](#production-deployment)

---

## 🎯 Overview

The Fleet Management System uses Docker for containerized deployment with two main services:

1. **PostgreSQL Database** - Data persistence layer
2. **FastAPI Application** - REST API and web interface

### Benefits

- ✅ Consistent development environment
- ✅ Easy deployment and scaling
- ✅ Isolated dependencies
- ✅ Production-ready configuration
- ✅ Automatic health checks and restart policies

---

## 📦 Prerequisites

### Required Software

- **Docker Engine** 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose** v2.0+ (included with Docker Desktop)

### Verify Installation

```bash
# Check Docker version
docker --version
# Docker version 24.0.0 or higher

# Check Docker Compose version
docker compose version
# Docker Compose version v2.20.0 or higher
```

---

## 🚀 Quick Start

### 1. Clone and Navigate

```bash
cd /path/to/fleet-management-system
```

### 2. Build and Start Containers

```bash
# Build images and start services
docker compose up --build

# Or run in detached mode (background)
docker compose up -d --build
```

### 3. Access the Application

- **Web Interface:** http://localhost:5000
- **API Documentation:** http://localhost:5000/docs
- **Database:** localhost:5432

### 4. Stop Containers

```bash
# Stop and remove containers
docker compose down

# Stop, remove containers, and delete volumes (⚠️ deletes all data)
docker compose down -v
```

---

## ⚙️ Docker Configuration

### File Structure

```
.
├── Dockerfile              # Application container definition
├── docker-compose.yml      # Multi-container orchestration
├── requirements.txt        # Python dependencies
└── .dockerignore           # Files to exclude from build
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/static /app/modules

EXPOSE 5000

CMD ["python", "main.py"]
```

### docker-compose.yml

```yaml
services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: fleet_management_db
    restart: unless-stopped
    environment:
      POSTGRES_USER: fleetuser
      POSTGRES_PASSWORD: fleetpass
      POSTGRES_DB: fleet_management
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fleetuser"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI Application
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: fleet_management_api
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://fleetuser:fleetpass@db:5432/fleet_management
    ports:
      - "5000:5000"
    volumes:
      - ./logs:/app/logs

volumes:
  postgres_data:

networks:
  fleet_network:
    driver: bridge
```

---

## 🔐 Environment Variables

### Database Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | fleetuser | PostgreSQL username |
| `POSTGRES_PASSWORD` | fleetpass | PostgreSQL password |
| `POSTGRES_DB` | fleet_management | Database name |
| `PGDATA` | /var/lib/postgresql/data/pgdata | Data directory |

### Application Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | postgresql://... | Full database connection string |
| `JWT_SECRET_KEY` | dev-secret-key | JWT signing key (⚠️ change in production) |
| `JWT_ALGORITHM` | HS256 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Token expiration time |

### Setting Custom Variables

Create a `.env` file in the project root:

```env
# Database
POSTGRES_USER=customuser
POSTGRES_PASSWORD=securepassword
POSTGRES_DB=fleet_db

# Application
JWT_SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Then reference in `docker-compose.yml`:

```yaml
api:
  env_file:
    - .env
```

---

## 🏗️ Container Architecture

### Network Topology

```
┌──────────────────────────────────────────────────┐
│  Host Machine (localhost)                        │
│  ┌────────────────────────────────────────────┐  │
│  │  Docker Network (fleet_network)            │  │
│  │                                            │  │
│  │  ┌──────────────────┐  ┌───────────────┐  │  │
│  │  │ fleet_mgmt_api   │  │ fleet_mgmt_db │  │  │
│  │  │                  │  │               │  │  │
│  │  │ Port: 5000       │  │ Port: 5432    │  │  │
│  │  │ Health: /health  │  │ pg_isready    │  │  │
│  │  │                  │──▶│               │  │  │
│  │  └──────────────────┘  └───────────────┘  │  │
│  │         ▲                      ▲          │  │
│  └─────────┼──────────────────────┼──────────┘  │
│            │                      │             │
│       Port 5000              Port 5432          │
└────────────┼──────────────────────┼─────────────┘
             │                      │
         Browser                Database
                                Client
```

### Volume Mounts

| Container | Mount | Purpose |
|-----------|-------|---------|
| api | `./logs:/app/logs` | Application logs persistence |
| api | `./backend:/app/backend` | Hot-reload backend code (dev) |
| api | `./main.py:/app/main.py` | Hot-reload main file (dev) |
| db | `postgres_data:/var/lib/postgresql/data` | Database persistence |

---

## 🔧 Docker Commands

### Build & Start

```bash
# Build and start all services
docker compose up --build

# Start in detached mode (background)
docker compose up -d

# Rebuild single service
docker compose up --build api
```

### Stop & Remove

```bash
# Stop services (keeps containers)
docker compose stop

# Stop and remove containers
docker compose down

# Remove containers and volumes (⚠️ deletes data)
docker compose down -v

# Remove everything including images
docker compose down -v --rmi all
```

### Logs & Debugging

```bash
# View logs from all services
docker compose logs

# Follow logs in real-time
docker compose logs -f

# View logs from specific service
docker compose logs api
docker compose logs db

# View last 100 lines
docker compose logs --tail=100 api
```

### Container Management

```bash
# List running containers
docker compose ps

# Execute command in running container
docker compose exec api bash
docker compose exec db psql -U fleetuser -d fleet_management

# Restart specific service
docker compose restart api

# View container resource usage
docker compose stats
```

### Database Operations

```bash
# Connect to PostgreSQL
docker compose exec db psql -U fleetuser -d fleet_management

# Create database backup
docker compose exec db pg_dump -U fleetuser fleet_management > backup.sql

# Restore database from backup
docker compose exec -T db psql -U fleetuser -d fleet_management < backup.sql

# Reset database (⚠️ deletes all data)
docker compose down -v
docker compose up -d db
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error:**
```
Error: bind: address already in use
```

**Solution:**
```bash
# Check what's using the port
sudo lsof -i :5000
sudo lsof -i :5432

# Stop the conflicting service or change ports in docker-compose.yml
ports:
  - "5001:5000"  # Map to different host port
```

#### 2. Database Connection Failed

**Error:**
```
could not connect to server: Connection refused
```

**Solution:**
```bash
# Check database health
docker compose ps

# View database logs
docker compose logs db

# Restart database
docker compose restart db

# Wait for healthy status
docker compose up -d db
# Wait 10-15 seconds for initialization
```

#### 3. Permission Denied Errors

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Fix directory permissions
sudo chown -R $USER:$USER ./logs ./static

# Or run Docker with appropriate permissions
sudo docker compose up
```

#### 4. Module Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Rebuild container with fresh dependencies
docker compose build --no-cache api
docker compose up api
```

#### 5. Static Directory Not Found

**Error:**
```
RuntimeError: Directory 'static' does not exist
```

**Solution:**
```bash
# Create static directory with .gitkeep
mkdir -p static modules
echo "# Keep directory" > static/.gitkeep

# Rebuild
docker compose up --build
```

### Health Checks

```bash
# Check API health
curl http://localhost:5000/health

# Check database health
docker compose exec db pg_isready -U fleetuser

# View health status
docker compose ps
```

### Reset Everything

```bash
# Nuclear option: remove everything and start fresh
docker compose down -v
docker system prune -a
rm -rf logs/*
docker compose up --build
```

---

## 🚀 Production Deployment

### Security Hardening

#### 1. Change Default Credentials

```yaml
environment:
  POSTGRES_USER: ${DB_USER}
  POSTGRES_PASSWORD: ${DB_PASSWORD}
  JWT_SECRET_KEY: ${JWT_SECRET}
```

#### 2. Use Secrets Management

```yaml
services:
  api:
    secrets:
      - db_password
      - jwt_secret

secrets:
  db_password:
    file: ./secrets/db_password.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt
```

#### 3. Limit Resource Usage

```yaml
api:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
      reservations:
        cpus: '1'
        memory: 1G
```

### Production docker-compose.yml

```yaml
services:
  db:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - internal
    # Don't expose port to host in production

  api:
    build: .
    restart: always
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      JWT_SECRET_KEY: ${JWT_SECRET}
    ports:
      - "5000:5000"
    depends_on:
      - db
    networks:
      - internal
      - external
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    networks:
      - external

volumes:
  postgres_data:
    driver: local

networks:
  internal:
    driver: bridge
  external:
    driver: bridge
```

### Continuous Deployment

```bash
#!/bin/bash
# deploy.sh - Production deployment script

set -e

echo "🚀 Deploying Fleet Management System..."

# Pull latest code
git pull origin main

# Build with production config
docker compose -f docker-compose.prod.yml build --no-cache

# Stop old containers
docker compose -f docker-compose.prod.yml down

# Start new containers
docker compose -f docker-compose.prod.yml up -d

# Wait for health checks
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check health
docker compose -f docker-compose.prod.yml ps

echo "✅ Deployment complete!"
```

---

## 📊 Monitoring

### Log Aggregation

```yaml
api:
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
```

### Metrics Collection

```bash
# Export metrics
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

---

## 🔗 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Python Docker Image](https://hub.docker.com/_/python)

---

## 📝 Changelog

### 2025-09-30 - v1.1.0
- ✅ Removed obsolete `version` attribute from docker-compose.yml
- ✅ Added automatic directory creation in Dockerfile
- ✅ Added existence checks for static/modules directories in main.py
- ✅ Created DOCKER.md documentation
- ✅ Fixed RuntimeError: Directory 'static' does not exist

### 2025-09-29 - v1.0.0
- Initial Docker configuration
- PostgreSQL 15 Alpine image
- Python 3.11 slim image
- Health checks for both services
- Volume persistence for database

---

**Last Updated:** September 30, 2025  
**Docker Compose Version:** v2.0+  
**Maintainer:** Development Team
