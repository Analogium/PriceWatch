# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**PriceWatch** is a price tracking application with automatic notifications. It monitors product prices from e-commerce sites (Amazon, Fnac, Darty) and sends email alerts when prices drop below user-defined thresholds.

**Tech Stack:**
- Backend: FastAPI (Python 3.12)
- Database: PostgreSQL + SQLAlchemy ORM
- Task Queue: Celery + Redis
- Containerization: Docker + Docker Compose
- Testing: pytest with full mocking

## Key Commands

### Development

```bash
# Start all services (backend, PostgreSQL, Redis, Celery)
docker-compose up -d

# View backend logs
docker-compose logs -f backend

# Access backend shell
docker-compose exec backend bash

# Stop all services
docker-compose down
```

### Testing

```bash
cd Backend

# Run ALL unit tests with coverage (in Docker - RECOMMENDED)
./run_unit_tests.sh

# Run specific test file
docker-compose exec backend python3 -m pytest tests/test_unit_scraper.py -v

# Run tests with specific marker
docker-compose exec backend python3 -m pytest tests/ -m unit -v
docker-compose exec backend python3 -m pytest tests/ -m email -v

# Run with coverage report
docker-compose exec backend python3 -m pytest tests/ --cov=app --cov-report=html -m unit
```

### Code Quality

```bash
cd Backend

# Run all linting checks
./run_linting.sh

# Format code with black
docker-compose exec backend black app/ tests/

# Check with flake8
docker-compose exec backend flake8 app/ tests/

# Sort imports
docker-compose exec backend isort app/ tests/

# Type checking
docker-compose exec backend mypy app/
```

### Database Migrations

```bash
cd Backend

# Create and apply a new migration
./migrate.sh "description of changes"

# Reset database (WARNING: deletes all data)
./reset_db.sh

# Check current migration version
docker-compose exec backend alembic current

# View migration history
docker-compose exec backend alembic history
```

## Architecture

### High-Level Structure

```
Backend/
├── app/
│   ├── api/
│   │   ├── dependencies.py           # Auth & DB dependencies
│   │   └── endpoints/
│   │       ├── auth.py               # JWT auth, registration, login, password reset
│   │       └── products.py           # Product CRUD, price history, pagination
│   ├── core/
│   │   ├── config.py                 # Settings (loaded from .env)
│   │   ├── security.py               # JWT, password hashing, validation
│   │   └── rate_limit.py             # Redis-based rate limiting
│   ├── db/
│   │   └── base.py                   # SQLAlchemy base and session
│   ├── models/                       # SQLAlchemy ORM models
│   │   ├── user.py                   # User model (auth, verification, reset tokens)
│   │   ├── product.py                # Product model
│   │   └── price_history.py         # Price history tracking
│   ├── schemas/                      # Pydantic validation schemas
│   │   ├── user.py
│   │   ├── product.py
│   │   └── price_history.py
│   ├── services/                     # Business logic
│   │   ├── scraper.py                # Web scraping (BeautifulSoup)
│   │   ├── email.py                  # SMTP email sending
│   │   └── price_history.py         # Price tracking logic
│   └── main.py                       # FastAPI app entry point
├── tasks.py                          # Celery tasks (price checking)
├── tests/
│   ├── test_unit_*.py                # Unit tests (pytest + mocks)
│   └── test_*.py                     # Integration tests (optional, require running server)
└── migrations/                       # Alembic database migrations
```

### Key Design Patterns

1. **Dependency Injection**: FastAPI's `Depends()` for database sessions and authentication
2. **Service Layer**: Business logic isolated in `services/` (scraper, email, price_history)
3. **Repository Pattern**: SQLAlchemy ORM models act as repositories
4. **Background Tasks**: Celery for async price checking (runs every 24h by default)
5. **Singleton Services**: Email and scraper services use singleton pattern for efficiency

### Authentication Flow

1. User registers → `POST /api/v1/auth/register`
   - Password strength validation (8+ chars, uppercase, lowercase, digit, special char)
   - Password hashed with bcrypt
   - Optional: Verification email sent with token

2. User logs in → `POST /api/v1/auth/login`
   - Returns JWT access token (30 min) + refresh token (7 days)
   - Tokens created in `core/security.py`

3. Protected endpoints check token → `Depends(get_current_user)`
   - Decodes JWT and loads user from database
   - Returns 401 if invalid/expired

4. Token refresh → `POST /api/v1/auth/refresh`
   - Accepts refresh token, returns new access token

### Price Tracking Flow

1. User adds product → `POST /api/v1/products`
   - URL is scraped immediately (`services/scraper.py`)
   - Product info (name, price, image) extracted
   - Saved to database with `target_price`
   - Initial price recorded in `price_history`

2. Celery Beat triggers `check_all_prices` every 24h
   - Defined in `tasks.py`
   - Iterates through all products
   - Scrapes current price
   - Records price change in `price_history` (if changed)
   - Sends email alert if `current_price <= target_price`

3. User views history → `GET /api/v1/products/{id}/history`
   - Returns time-series price data
   - Can request statistics (min, max, avg, % change)

### Testing Strategy

**All tests are unit tests with full mocking** - no external dependencies required.

- **Test markers**: `@pytest.mark.unit`, `@pytest.mark.scraper`, `@pytest.mark.email`, `@pytest.mark.celery`
- **Mocking**: Uses `unittest.mock` to mock database, HTTP requests, SMTP
- **Coverage**: 70%+ total, 100% on services
- **Run in Docker**: Tests execute in backend container for consistency

**Test files:**
- `test_unit_scraper.py` (17 tests) - Web scraping with mocked HTTP responses
- `test_unit_email.py` (13 tests) - Email sending with mocked SMTP
- `test_unit_price_history.py` (13 tests) - Price tracking logic with mocked DB
- `test_unit_celery_tasks.py` (11 tests) - Celery tasks with mocked everything
- `test_unit_security.py` (9 tests) - Password validation, token generation

### Common Patterns

**Adding a new endpoint:**
1. Define Pydantic schema in `schemas/`
2. Add endpoint function in `api/endpoints/`
3. Use `Depends(get_current_user)` for authenticated routes
4. Use `Depends(get_db)` for database access
5. Write unit tests in `tests/test_unit_*.py`

**Adding a model field:**
1. Modify model in `models/`
2. Create migration: `./migrate.sh "add field description"`
3. Update corresponding Pydantic schema in `schemas/`
4. Update tests

**Testing with mocks:**
```python
@pytest.mark.unit
@patch('app.services.scraper.requests.get')
def test_scrape_amazon(mock_get):
    mock_get.return_value.content = b"<html>...</html>"
    mock_get.return_value.status_code = 200

    result = scraper.scrape_amazon("https://amazon.fr/...")
    assert result.price == 199.99
```

### Important Configuration

**Environment variables** (`.env`):
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key (generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` - Email configuration
- `REDIS_URL` - Redis for Celery and rate limiting
- `ACCESS_TOKEN_EXPIRE_MINUTES=30` - JWT expiry
- `REFRESH_TOKEN_EXPIRE_DAYS=7` - Refresh token expiry

**API Pagination:**
All product list endpoints support:
- `?page=1&page_size=20` - Pagination
- `?search=query` - Search by name/URL
- `?sort_by=current_price&sort_order=asc` - Sorting
- Can combine: `?page=1&search=laptop&sort_by=price&sort_order=desc`

### Known Quirks

1. **SQLAlchemy model comparisons**: Use `is` instead of `==` when comparing model classes in tests to avoid triggering SQLAlchemy's `__eq__` operator
   ```python
   # Correct
   if args[0] is Product:

   # Wrong (causes SQLAlchemy error)
   if args[0] == Product:
   ```

2. **Email HTML encoding**: Email bodies are base64-encoded by MIME. In tests, decode with:
   ```python
   html_content = payload[0].get_payload(decode=True).decode('utf-8')
   ```

3. **Celery Beat persistence**: Schedule state is not persisted. Restarting containers resets the schedule.

4. **Scraping fragility**: Site HTML structure changes break scrapers. Add retry logic and error handling.

5. **User model password**: The model has `password_hash` field, not `password`. Never use `User(password_hash=...)` in tests; use `Mock(spec=User)` with manual attribute setting.

### Deployment Notes

- Docker Compose is configured for development
- For production: use separate containers, external PostgreSQL, Redis cluster
- Enable HTTPS/SSL for production API
- Set up proper log rotation and monitoring
- Configure Celery worker scaling based on load
- Rate limiting is per-IP (100 req/min by default)

### Documentation Files

- `README.md` - Setup and quick start
- `RoadMapDoc/RoadMap.md` - Feature roadmap and implementation status
- `RoadMapDoc/TESTING.md` - Testing infrastructure documentation
- `RoadMapDoc/SECURITY_FEATURES.md` - Security features documentation

### When Making Changes

1. Write unit tests first (TDD encouraged)
2. Run `./run_unit_tests.sh` to ensure tests pass
3. Run `./run_linting.sh` to check code quality
4. Update relevant documentation in `RoadMapDoc/`
5. For new features, mark as completed in `RoadMap.md`
6. For API changes, test with Swagger UI at `/docs`
