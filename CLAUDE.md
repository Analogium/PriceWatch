# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PriceWatch is a price monitoring application that tracks product prices from e-commerce websites and sends notifications when prices drop below target thresholds. Built with FastAPI, PostgreSQL, Redis, and Celery for background task processing.

## Development Commands

All commands run via Docker Compose. Start services first with `docker-compose up -d`.

### Testing

```bash
# Run unit tests with coverage (requires services running)
./Backend/run_unit_tests.sh

# Run single test file
docker-compose exec backend python3 -m pytest tests/test_unit_auth_endpoints.py -v -m unit

# Run specific test
docker-compose exec backend python3 -m pytest tests/test_unit_auth_endpoints.py::TestRegister::test_register_success -v
```

Tests use `@pytest.mark.unit` for unit tests and `@pytest.mark.scraper` for scraper tests. Coverage threshold is 70%.

### Linting and Formatting

```bash
# Run all linting checks
./Backend/run_linting.sh

# Inside container
docker-compose exec backend python3 -m black --check app/ tests/
docker-compose exec backend python3 -m isort --check-only app/ tests/
docker-compose exec backend python3 -m flake8 app/ tests/
docker-compose exec backend python3 -m mypy app/ tasks.py

# Auto-fix formatting
docker-compose exec backend python3 -m black app/ tests/
docker-compose exec backend python3 -m isort app/ tests/
```

### Database Migrations

```bash
# Generate and apply migration
./Backend/migrate.sh "migration message"

# Manual migration commands
docker-compose exec -T backend alembic revision --autogenerate -m "message"
docker-compose exec -T backend alembic upgrade head
docker-compose exec -T backend alembic current
```

## Architecture

### Backend Structure

- **app/api/endpoints/** - FastAPI route handlers (auth, products, admin, health, preferences)
- **app/api/dependencies.py** - Dependency injection (auth, database sessions)
- **app/core/** - Configuration, security (JWT, password hashing), rate limiting, logging
- **app/models/** - SQLAlchemy ORM models (user, product, price_history, scraping_stats, user_preferences)
- **app/schemas/** - Pydantic validation schemas
- **app/services/** - Business logic (scraper, playwright_scraper, email, price_history, admin)
- **app/db/base.py** - SQLAlchemy engine and session configuration
- **tasks.py** - Celery task definitions for background price checking

### Services (Docker Compose)

- **backend** - FastAPI app (port 8000)
- **db** - PostgreSQL 15 (port 5432)
- **redis** - Redis 7 for Celery broker (port 6379)
- **celery_worker** - Background task processor
- **celery_beat** - Scheduled task scheduler
- **pgadmin** - Database admin UI (port 5050)
- **redis_commander** - Redis admin UI (port 8081)

### Scraping System

Two scraper implementations exist:
- `services/scraper.py` - Basic HTTP scraper using requests/BeautifulSoup
- `services/playwright_scraper.py` - Browser-based scraper for JavaScript-rendered sites

Scraping runs in parallel batches controlled by `MAX_PARALLEL_SCRAPERS` and `SCRAPING_BATCH_SIZE` settings.

## Code Style

- Line length: 120 characters
- Python 3.12 target
- Black formatting, isort imports, flake8 linting, mypy type checking
- Exclude migrations/alembic from linting

## API Structure

All endpoints prefixed with `/api/v1/`:
- `/auth` - Authentication (register, login, me)
- `/products` - Product CRUD and price checking
- `/users` - User preferences
- `/admin` - Admin features
- `/health` - Health check (no prefix)

## Environment Variables

Required in `Backend/.env`:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_FROM` - Email config
- `REDIS_URL` - Redis connection (default: redis://localhost:6379/0)

Optional:
- `SENTRY_DSN` - Error monitoring
- `LOG_LEVEL`, `LOG_DIR`, `ENABLE_JSON_LOGS`, `ENABLE_LOG_ROTATION` - Logging config
