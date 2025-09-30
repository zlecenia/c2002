.PHONY: help install run test clean docker-up docker-down docker-logs backup restore

PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
DOCKER_COMPOSE := docker compose

BACKUP_DIR := backups
SCRIPTS_DIR := scripts

help:
	@echo "======================================"
	@echo "Fleet Management System - Makefile"
	@echo "======================================"
	@echo ""
	@echo "📦 SETUP & INSTALLATION"
	@echo "  make install          Install all dependencies"
	@echo "  make venv             Create Python virtual environment"
	@echo "  make deps             Install Python dependencies only"
	@echo ""
	@echo "🚀 APPLICATION"
	@echo "  make run              Run the FastAPI application"
	@echo "  make dev              Run in development mode (auto-reload)"
	@echo "  make seed             Initialize database with sample data"
	@echo "  make reset            Reset database (drop all data)"
	@echo ""
	@echo "🗄️  DATABASE OPERATIONS"
	@echo "  make backup           Create database backup (Docker)"
	@echo "  make backup-local     Create database backup (Local PostgreSQL)"
	@echo "  make backup-list      List all available backups"
	@echo "  make restore FILE=... Restore database from backup file"
	@echo "  make db-prune         Remove old backups (keep last 10)"
	@echo "  make psql             Connect to PostgreSQL shell (Docker)"
	@echo "  make psql-local       Connect to PostgreSQL shell (Local)"
	@echo ""
	@echo "🐳 DOCKER OPERATIONS"
	@echo "  make docker-build     Build Docker images"
	@echo "  make docker-up        Start all containers"
	@echo "  make docker-down      Stop all containers"
	@echo "  make docker-restart   Restart all containers"
	@echo "  make docker-logs      Show container logs"
	@echo "  make docker-logs-api  Show API logs only"
	@echo "  make docker-logs-db   Show database logs only"
	@echo "  make docker-ps        Show container status"
	@echo "  make docker-clean     Remove containers and volumes"
	@echo "  make docker-shell     Open shell in API container"
	@echo ""
	@echo "🧪 TESTING & QA"
	@echo "  make test             Run all tests"
	@echo "  make test-auth        Run authentication tests"
	@echo "  make test-api         Run API tests"
	@echo "  make test-modules     Run module tests"
	@echo "  make test-coverage    Run tests with coverage report"
	@echo "  make lint             Run code linting"
	@echo ""
	@echo "🛠️  UTILITIES"
	@echo "  make clean            Clean Python cache files"
	@echo "  make clean-all        Clean everything (cache, logs, backups)"
	@echo "  make format           Format code with black"
	@echo "  make format-check     Check code formatting"
	@echo "  make logs-clean       Clean application logs"
	@echo "  make requirements     Update requirements.txt"
	@echo ""
	@echo "📚 DOCUMENTATION"
	@echo "  make docs             Generate API documentation"
	@echo "  make docs-serve       Serve documentation locally"
	@echo ""
	@echo "======================================"

install: deps
	@echo "✅ Installation complete!"

venv:
	@echo "📦 Creating virtual environment..."
	$(PYTHON) -m venv venv
	@echo "✅ Virtual environment created"
	@echo "Run: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"

deps:
	@echo "📦 Installing Python dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✅ Dependencies installed"

run:
	@echo "🚀 Starting Fleet Management API..."
	$(PYTHON) main.py

dev:
	@echo "🚀 Starting FastAPI in development mode..."
	uvicorn main:app --reload --host 0.0.0.0 --port 5000

seed:
	@echo "🌱 Seeding database with sample data..."
	curl -X POST http://localhost:5000/api/v1/init-data
	@echo "✅ Database seeded"

reset:
	@echo "⚠️  WARNING: This will delete all database data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "\n🗑️  Resetting database..."; \
		$(DOCKER_COMPOSE) down -v; \
		$(DOCKER_COMPOSE) up -d db; \
		sleep 5; \
		echo "✅ Database reset complete"; \
	else \
		echo "\n❌ Reset cancelled"; \
	fi

backup:
	@echo "📦 Creating database backup (Docker)..."
	@bash $(SCRIPTS_DIR)/backup.sh --docker
	@echo "✅ Backup created"

backup-local:
	@echo "📦 Creating database backup (Local PostgreSQL)..."
	@bash $(SCRIPTS_DIR)/backup.sh --local
	@echo "✅ Backup created"

backup-list:
	@echo "======================================"
	@echo "📋 Available Database Backups"
	@echo "======================================"
	@if [ -d "$(BACKUP_DIR)" ] && [ "$$(ls -A $(BACKUP_DIR)/*.sql* 2>/dev/null)" ]; then \
		ls -lh $(BACKUP_DIR)/*.sql* | awk '{print $$9, "("$$5")"}' | sort -r; \
	else \
		echo "No backups found in $(BACKUP_DIR)/"; \
	fi
	@echo "======================================"

restore:
	@if [ -z "$(FILE)" ]; then \
		echo "❌ ERROR: FILE parameter is required"; \
		echo "Usage: make restore FILE=backups/fleet_management_YYYYMMDD_HHMMSS.sql.gz"; \
		exit 1; \
	fi
	@echo "📥 Restoring database from $(FILE)..."
	@bash $(SCRIPTS_DIR)/restore.sh --docker --yes $(FILE)
	@echo "✅ Database restored"

restore-local:
	@if [ -z "$(FILE)" ]; then \
		echo "❌ ERROR: FILE parameter is required"; \
		echo "Usage: make restore-local FILE=backups/fleet_management_YYYYMMDD_HHMMSS.sql.gz"; \
		exit 1; \
	fi
	@echo "📥 Restoring database from $(FILE)..."
	@bash $(SCRIPTS_DIR)/restore.sh --local --yes $(FILE)
	@echo "✅ Database restored"

db-prune:
	@echo "🗑️  Pruning old backups..."
	@bash $(SCRIPTS_DIR)/backup.sh --help | grep -A1 "MAX_BACKUPS"
	@find $(BACKUP_DIR) -name "*.sql*" -type f | sort -r | tail -n +11 | xargs rm -f 2>/dev/null || true
	@echo "✅ Old backups removed"

psql:
	@echo "🔌 Connecting to PostgreSQL (Docker)..."
	$(DOCKER_COMPOSE) exec db psql -U fleetuser -d fleet_management

psql-local:
	@echo "🔌 Connecting to PostgreSQL (Local)..."
	@if [ -z "$$DATABASE_URL" ]; then \
		echo "❌ ERROR: DATABASE_URL not set"; \
		exit 1; \
	fi
	psql $$DATABASE_URL

docker-build:
	@echo "🐳 Building Docker images..."
	$(DOCKER_COMPOSE) build --no-cache
	@echo "✅ Images built"

docker-up:
	@echo "🐳 Starting Docker containers..."
	$(DOCKER_COMPOSE) up -d
	@echo "✅ Containers started"
	@echo ""
	@$(MAKE) docker-ps

docker-down:
	@echo "🐳 Stopping Docker containers..."
	$(DOCKER_COMPOSE) down
	@echo "✅ Containers stopped"

docker-restart:
	@echo "🔄 Restarting Docker containers..."
	$(DOCKER_COMPOSE) restart
	@echo "✅ Containers restarted"

docker-logs:
	@echo "📋 Showing container logs..."
	$(DOCKER_COMPOSE) logs -f

docker-logs-api:
	@echo "📋 Showing API logs..."
	$(DOCKER_COMPOSE) logs -f api

docker-logs-db:
	@echo "📋 Showing database logs..."
	$(DOCKER_COMPOSE) logs -f db

docker-ps:
	@echo "======================================"
	@echo "🐳 Docker Container Status"
	@echo "======================================"
	@$(DOCKER_COMPOSE) ps
	@echo "======================================"

docker-clean:
	@echo "⚠️  WARNING: This will remove all containers and volumes!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "\n🗑️  Cleaning Docker environment..."; \
		$(DOCKER_COMPOSE) down -v --remove-orphans; \
		docker system prune -f; \
		echo "✅ Docker environment cleaned"; \
	else \
		echo "\n❌ Cleanup cancelled"; \
	fi

docker-shell:
	@echo "🐚 Opening shell in API container..."
	$(DOCKER_COMPOSE) exec api bash

test:
	@echo "🧪 Running all tests..."
	$(PYTEST) tests/ -v
	@echo "✅ Tests complete"

test-auth:
	@echo "🧪 Running authentication tests..."
	$(PYTEST) tests/test_auth.py -v

test-api:
	@echo "🧪 Running API tests..."
	$(PYTEST) tests/test_*.py -v --ignore=tests/test_modules.py

test-modules:
	@echo "🧪 Running module tests..."
	$(PYTEST) tests/test_modules.py -v

test-coverage:
	@echo "🧪 Running tests with coverage..."
	$(PYTEST) tests/ --cov=backend --cov-report=html --cov-report=term
	@echo "✅ Coverage report generated in htmlcov/"

lint:
	@echo "🔍 Running code linting..."
	@if command -v pylint >/dev/null 2>&1; then \
		pylint backend/ main.py; \
	else \
		echo "⚠️  pylint not installed. Install with: pip install pylint"; \
	fi

clean:
	@echo "🧹 Cleaning Python cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf htmlcov/ 2>/dev/null || true
	@echo "✅ Cache cleaned"

clean-all: clean
	@echo "🧹 Cleaning everything..."
	@rm -rf logs/*.log 2>/dev/null || true
	@rm -rf $(BACKUP_DIR)/*.sql* 2>/dev/null || true
	@rm -rf venv/ 2>/dev/null || true
	@echo "✅ Everything cleaned"

logs-clean:
	@echo "🧹 Cleaning application logs..."
	@rm -rf logs/*.log 2>/dev/null || true
	@mkdir -p logs
	@echo "✅ Logs cleaned"

format:
	@echo "🎨 Formatting code with black..."
	@if command -v black >/dev/null 2>&1; then \
		black backend/ main.py tests/; \
		echo "✅ Code formatted"; \
	else \
		echo "⚠️  black not installed. Install with: pip install black"; \
	fi

format-check:
	@echo "🎨 Checking code formatting..."
	@if command -v black >/dev/null 2>&1; then \
		black --check backend/ main.py tests/; \
	else \
		echo "⚠️  black not installed. Install with: pip install black"; \
	fi

requirements:
	@echo "📝 Updating requirements.txt..."
	$(PIP) freeze > requirements.txt
	@echo "✅ requirements.txt updated"

docs:
	@echo "📚 Generating API documentation..."
	@echo "OpenAPI docs available at: http://localhost:5000/docs"
	@echo "ReDoc available at: http://localhost:5000/redoc"

docs-serve:
	@echo "📚 Serving documentation..."
	@echo "Visit: http://localhost:5000/docs"
	@$(MAKE) run

.DEFAULT_GOAL := help
