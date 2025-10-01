# 🐳 Docker Documentation - Fleet Management System

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Makefile Usage](#makefile-usage)
- [Docker Configuration](#docker-configuration)
- [Environment Variables](#environment-variables)
- [Container Architecture](#container-architecture)
- [Docker Commands](#docker-commands)
- [Database Backup & Restore](#database-backup--restore)
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

## 🛠️ Makefile Usage

The project includes a comprehensive **Makefile** that simplifies common operations. This is the **recommended way** to interact with the system.

### Quick Reference

```bash
# Show all available commands
make help

# Docker operations
make docker-up          # Start containers
make docker-down        # Stop containers
make docker-logs        # View logs

# Database backup & restore
make backup             # Create backup
make backup-list        # List backups
make restore FILE=...   # Restore from backup

# Development
make run                # Run application
make test               # Run tests
make clean              # Clean cache
```

### Complete Command List

#### 📦 Setup & Installation
```bash
make install            # Install all dependencies
make venv               # Create Python virtual environment
make deps               # Install Python dependencies only
```

#### 🚀 Application
```bash
make run                # Run the FastAPI application
make dev                # Run in development mode (auto-reload)
make seed               # Initialize database with sample data
make reset              # Reset database (drop all data)
```

#### 🗄️ Database Operations
```bash
make backup             # Create database backup (Docker)
make backup-local       # Create database backup (Local PostgreSQL)
make backup-list        # List all available backups
make restore FILE=...   # Restore database from backup file
make db-prune           # Remove old backups (keep last 10)
make psql               # Connect to PostgreSQL shell (Docker)
make psql-local         # Connect to PostgreSQL shell (Local)
```

#### 🐳 Docker Operations
```bash
make docker-build       # Build Docker images
make docker-up          # Start all containers
make docker-down        # Stop all containers
make docker-restart     # Restart all containers
make docker-logs        # Show container logs (all)
make docker-logs-api    # Show API logs only
make docker-logs-db     # Show database logs only
make docker-ps          # Show container status
make docker-clean       # Remove containers and volumes
make docker-shell       # Open shell in API container
```

#### 🧪 Testing & QA
```bash
make test               # Run all tests
make test-auth          # Run authentication tests
make test-api           # Run API tests
make test-modules       # Run module tests
make test-coverage      # Run tests with coverage report
make lint               # Run code linting
```

#### 🛠️ Utilities
```bash
make clean              # Clean Python cache files
make clean-all          # Clean everything (cache, logs, backups)
make format             # Format code with black
make format-check       # Check code formatting
make logs-clean         # Clean application logs
make requirements       # Update requirements.txt
```

### Examples

#### Complete Development Workflow
```bash
# 1. Start Docker containers
make docker-up

# 2. Seed database with sample data
make seed

# 3. View logs
make docker-logs-api

# 4. Create a backup
make backup

# 5. Run tests
make test

# 6. Stop containers
make docker-down
```

#### Backup & Restore Workflow
```bash
# Create backup
make backup

# List all backups
make backup-list

# Restore from specific backup
make restore FILE=backups/fleet_management_20250930_120000.sql.gz

# Clean old backups (keep last 10)
make db-prune
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

# Reset database (⚠️ deletes all data)
docker compose down -v
docker compose up -d db
```

---

## 💾 Database Backup & Restore

The system includes automated scripts for database backup and restore operations with support for both Docker and local PostgreSQL installations.

### Quick Backup & Restore

```bash
# Using Makefile (recommended)
make backup                 # Create backup
make backup-list            # List backups
make restore FILE=backup.sql.gz  # Restore backup

# Using scripts directly
./scripts/backup.sh --docker
./scripts/restore.sh --docker backups/fleet_management_20250930_120000.sql.gz
```

### Backup Features

✅ **Automatic timestamped filenames** - `fleet_management_YYYYMMDD_HHMMSS.sql.gz`  
✅ **Gzip compression** - Reduced storage and faster transfers  
✅ **Retention policy** - Automatically keeps last 10 backups  
✅ **Docker & local support** - Works with both environments  
✅ **Verification** - File size and integrity checks  

### Creating Backups

#### Via Makefile (Recommended)

```bash
# Backup from Docker container
make backup

# Backup from local PostgreSQL
make backup-local

# List all backups
make backup-list
```

#### Via Script Directly

```bash
# Docker backup (compressed)
./scripts/backup.sh --docker

# Local PostgreSQL backup
./scripts/backup.sh --local

# Custom filename
./scripts/backup.sh --docker --file backups/my_backup.sql.gz

# Uncompressed backup
./scripts/backup.sh --docker --no-compress

# Verbose output
./scripts/backup.sh --docker --verbose
```

### Restoring Backups

⚠️ **WARNING:** Restore operations will **REPLACE ALL DATA** in the target database!

#### Via Makefile (Recommended)

```bash
# List available backups
make backup-list

# Restore specific backup (Docker)
make restore FILE=backups/fleet_management_20250930_120000.sql.gz

# Restore to local PostgreSQL
make restore-local FILE=backups/fleet_management_20250930_120000.sql.gz
```

#### Via Script Directly

```bash
# Restore to Docker container
./scripts/restore.sh --docker backups/fleet_management_20250930_120000.sql.gz

# Restore to local PostgreSQL
./scripts/restore.sh --local backups/fleet_management_20250930_120000.sql.gz

# Skip confirmation prompt
./scripts/restore.sh --docker --yes backups/latest.sql.gz

# Dry run (show what would be done)
./scripts/restore.sh --docker --dry-run backups/backup.sql.gz
```

### Backup Directory Structure

```
backups/
├── .gitignore                                    # Ignores *.sql files
├── README.md                                     # Backup documentation
├── fleet_management_20250930_120000.sql.gz      # Compressed backup
├── fleet_management_20250930_140000.sql.gz      # Another backup
└── ...
```

### Retention Policy

The system automatically manages backup retention:

- **Default:** Keep last 10 backups
- **Automatic pruning:** Runs after each backup
- **Manual pruning:** `make db-prune`
- **Custom retention:** Set `MAX_BACKUPS` environment variable

```bash
# Custom retention (keep 20 backups)
export MAX_BACKUPS=20
make backup
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | - | PostgreSQL connection string (local only) |
| `POSTGRES_USER` | fleetuser | PostgreSQL username (Docker) |
| `POSTGRES_DB` | fleet_management | Database name (Docker) |
| `MAX_BACKUPS` | 10 | Maximum backups to keep |

### Backup Strategies

#### Development
```bash
# Before major changes
make backup

# After successful migration
make backup
```

#### Production
```bash
# Daily backup (cron job)
0 2 * * * cd /path/to/project && make backup

# Before deployment
make backup

# After deployment verification
make backup
```

### PostgreSQL Shell Access

```bash
# Docker container
make psql

# Local PostgreSQL
make psql-local

# Or directly
docker compose exec db psql -U fleetuser -d fleet_management
```

### Manual Database Operations

```bash
# Connect to PostgreSQL shell
make psql

# List all databases
\l

# List all tables
\dt

# Describe table structure
\d table_name

# Run SQL query
SELECT * FROM users LIMIT 10;

# Exit
\q
```

### Backup Best Practices

1. **Regular Backups** - Schedule daily automated backups
2. **Before Changes** - Always backup before schema migrations
3. **Test Restores** - Periodically test restore procedures
4. **Off-site Storage** - Copy critical backups to external storage
5. **Retention Policy** - Balance storage costs with recovery needs
6. **Documentation** - Keep notes on important backup timestamps

### Troubleshooting Backups

#### Backup Script Fails

```bash
# Check Docker container is running
docker compose ps

# Check disk space
df -h

# Verify permissions
ls -la backups/

# Run with verbose output
./scripts/backup.sh --docker --verbose
```

#### Restore Fails

```bash
# Verify backup file exists
ls -lh backups/

# Check file integrity (compressed)
gunzip -t backups/fleet_management_20250930_120000.sql.gz

# Dry run to test
./scripts/restore.sh --docker --dry-run backups/backup.sql.gz
```

#### Container Not Running

```bash
# Start containers
make docker-up

# Wait for database to be ready
sleep 10

# Try backup again
make backup
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
