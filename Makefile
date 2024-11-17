.PHONY: rebuild clean build up down test rebuildDb

# Default target
all: rebuild

# Full rebuild of the application
rebuild: clean build up

# Clean up Docker resources
clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v
	docker system prune -f

# Build containers
build:
	@echo "🏗️  Building containers..."
	docker-compose build --no-cache

# Start services
up:
	@echo "🚀 Starting services..."
	docker-compose up

# Stop services
down:
	@echo "⏹️  Stopping services..."
	docker-compose down

# Reinitialize database only
rebuildDb:
	@echo "🗄️  Creating fresh database..."
	docker-compose down -v
	rm -rf data/patent_db.sqlite
	docker-compose up -d
	@echo "Waiting for containers to start..."
	@sleep 5  # Give containers time to start
	docker exec -it patent-mini-app-backend-1 python -c "from api.database.database import init_db; init_db(fresh=True)"

updateDb:
	@echo "🔄 Updating database schema..."
	docker-compose up -d
	@echo "Waiting for containers to start..."
	@sleep 5  # Give containers time to start"
	docker exec -it patent-mini-app-backend-1 python -c "from api.database.database import init_db; init_db(fresh=False)"

# Run tests
test:
	@echo "🧪 Running tests..."
	docker-compose run patent-mini-app-backend-1 pytest

# Show help
help:
	@echo "Available commands:"
	@echo "  make rebuild    - Clean, rebuild and start services"
	@echo "  make clean     - Clean up Docker resources"
	@echo "  make build     - Build containers"
	@echo "  make up        - Start services"
	@echo "  make down      - Stop services"
	@echo "  make rebuildDb - Reinitialize database only"
	@echo "  make test      - Run all tests"