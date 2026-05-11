.PHONY: help up down build restart logs init-db seed-db test lint format clean logs-api logs-dashboard logs-airflow logs-mlflow dbt-run dbt-test shell-db shell-minio ci-setup install-hooks

# Colors
GREEN  := \033[0;32m
YELLOW := \033[0;33m
NC     := \033[0m

export COMPOSE_FILE := docker-compose.yml
export ENV_FILE    := .env

# =============================================================================
# HELP
# =============================================================================
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# =============================================================================
# DOCKER OPERATIONS
# =============================================================================
up: ## Start all services
	docker compose up -d
	@echo "$(GREEN)✓ All services started. Access points:$(NC)"
	@echo "  FastAPI:    http://localhost:8000"
	@echo "  Streamlit:  http://localhost:8501"
	@echo "  Airflow:    http://localhost:8080"
	@echo "  MLflow:     http://localhost:5001"
	@echo "  MinIO:      http://localhost:9001"
	@echo "  PgAdmin:    http://localhost:5050"

down: ## Stop and remove all containers
	docker compose down --volumes --remove-orphans

build: ## Build all images
	docker compose build --parallel

restart: ## Restart all services
	docker compose restart

logs: ## Tail logs from all services
	docker compose logs -f

logs-api: ## Tail FastAPI logs
	docker compose logs -f fastapi

logs-dashboard: ## Tail Streamlit logs
	docker compose logs -f streamlit

logs-airflow: ## Tail Airflow logs
	docker compose logs -f airflow-webserver

logs-mlflow: ## Tail MLflow logs
	docker compose logs -f mlflow

# =============================================================================
# DATABASE
# =============================================================================
init-db: ## Initialize database with schema
	docker compose exec -T postgres psql -U dealsense_user -d dealsense -f /docker-entrypoint-initdb.d/init.sql

seed-db: ## Seed database with sample data
	docker compose exec -T postgres psql -U dealsense_user -d dealsense -f /docker-entrypoint-initdb.d/seed.sql

shell-db: ## Open psql shell
	docker compose exec postgres psql -U dealsense_user -d dealsense

shell-minio: ## Open MinIO client shell
	docker compose exec minio mc alias set dealsense http://minio:9000 minioadmin minioadmin_change_in_production

# =============================================================================
# TESTING
# =============================================================================
test: ## Run all tests
	docker compose exec -T api pytest /app/tests -v --cov=/app/src --cov-report=xml

test-coverage: ## Run tests with coverage report
	docker compose exec -T api pytest /app/tests -v --cov=/app/src --cov-report=html --cov-report=term

# =============================================================================
# CODE QUALITY
# =============================================================================
lint: ## Run ruff linter
	docker compose exec -T api ruff check /app/src /app/tests

format: ## Run ruff and black formatter
	docker compose exec -T api ruff format /app/src /app/tests
	docker compose exec -T api black --line-length=100 /app/src /app/tests

# =============================================================================
# DBT
# =============================================================================
dbt-run: ## Run dbt transformations
	docker compose exec -T dbt dbt run --project-dir /app/dbt

dbt-test: ## Run dbt tests
	docker compose exec -T dbt dbt test --project-dir /app/dbt

dbt-docs: ## Generate dbt documentation
	docker compose exec -T dbt dbt docs generate --project-dir /app/dbt

# =============================================================================
# DEVELOPMENT
# =============================================================================
clean: ## Remove all Docker volumes and containers
	docker compose down -v --remove-orphans
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true

ci-setup: ## Install pre-commit hooks
	pre-commit install

install-hooks: ci-setup

# =============================================================================
# ML / MODEL OPERATIONS
# =============================================================================
mlflow: ## Open MLflow UI
	@echo "MLflow tracking server: http://localhost:5001"

train-model: ## Run ML training pipeline
	docker compose exec -T api python -m src.models.train

# =============================================================================
# SCRAPING
# =============================================================================
run-scraper: ## Run the Scrapy spider
	docker compose exec scraper scrapy crawl ma_deals

# =============================================================================
# API / DASHBOARD
# =============================================================================
api-reload: ## Reload FastAPI (for development)
	docker compose exec -T fastapi kill -HUP 1

dashboard-reload: ## Reload Streamlit
	docker compose exec -T streamlit kill -HUP 1