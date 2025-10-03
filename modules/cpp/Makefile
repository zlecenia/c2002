.PHONY: help build up down restart logs clean test

help:
	@echo "Connect++ (CPP) - Make Commands"
	@echo ""
	@echo "  make build     - Build Docker images"
	@echo "  make up        - Start all services"
	@echo "  make down      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo "  make logs      - View logs (all services)"
	@echo "  make clean     - Stop and remove volumes"
	@echo "  make test      - Run tests"
	@echo "  make dev       - Start in development mode"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8080"
	@echo "API Docs: http://localhost:8080/docs"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	@echo "✅ Cleaned up all containers and volumes"

test:
	@echo "🧪 Running backend tests..."
	@docker-compose exec -T backend pytest tests/ -v
	@echo ""
	@echo "✅ All tests completed!"

dev:
	docker-compose up

status:
	docker-compose ps

shell-backend:
	docker-compose exec backend bash

shell-db:
	docker-compose exec postgres psql -U cppuser -d cppdb
