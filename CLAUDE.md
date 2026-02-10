# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**PriceWatch** is a price monitoring application with automatic notifications. Users can track product prices from multiple French e-commerce sites (Amazon.fr, Fnac, Darty, Cdiscount, Boulanger, E.Leclerc) and receive email alerts when prices drop below their target.

### Tech Stack
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, PostgreSQL, Redis
- **Frontend**: React 19 + TypeScript, Vite, TailwindCSS, React Query
- **Background Tasks**: Celery with Redis broker
- **Web Scraping**: BeautifulSoup (HTTP) + Playwright (browser automation for anti-bot protection)
- **Container Orchestration**: Docker Compose

## Architecture

### Backend Architecture

The backend follows a layered architecture with clear separation of concerns:

**Core Layers:**
- `app/api/endpoints/` - HTTP route handlers organized by domain (auth, products, admin, preferences, health)
- `app/services/` - Business logic layer (scraper, email, price_history, admin)
- `app/models/` - SQLAlchemy ORM models (User, Product, PriceHistory, UserPreferences, ScrapingStats)
- `app/schemas/` - Pydantic schemas for validation and serialization
- `app/core/` - Cross-cutting concerns (config, security, rate_limit, logging)
- `app/db/` - Database configuration and session management

**Key Services:**
- **Scraper Service** (`app/services/scraper.py`): HTTP-based scraping with BeautifulSoup for each supported e-commerce site. Includes detailed price parsing that handles both comma (14,34 €) and dot (14.34) decimal separators.
- **Playwright Scraper** (`app/services/playwright_scraper.py`): Fallback browser automation scraper for sites with anti-bot protection (CAPTCHA, Cloudflare). Uses realistic browser settings and human-like delays.
- **Email Service** (`app/services/email.py`): SMTP email notifications respecting user preferences
- **Price History Service** (`app/services/price_history.py`): Tracks price changes with deduplication logic
- **Admin Service** (`app/services/admin.py`): Admin-specific operations and statistics
- **Advanced Scraping** (`app/services/scraper_advanced.py`): User-Agent rotation, Redis-based response caching, circuit breaker pattern, and proxy support utilities used by the scrapers

**Background Tasks:**
- `tasks.py` - Celery tasks for periodic price checking with configurable frequency per product (daily, hourly, every 6h, every 12h)
- Parallel scraping using ThreadPoolExecutor for improved performance
- Product availability tracking with automatic status updates

### Frontend Architecture

React application with modern patterns:
- **React Query** for server state management and caching
- **Zustand** for client state (authentication via AuthContext)
- **React Hook Form + Zod** for form validation
- **React Router v7** for routing with protected/public route components
- **Recharts** for price history visualization
- Context providers: AuthContext, ToastContext, PriceCheckContext
- Layout system with Header, Footer, and main Layout wrapper

### Database Schema

**Key Tables:**
- `users` - User accounts with hashed passwords, email verification, and admin flags
- `products` - Tracked products with current_price, target_price, check_frequency, is_available
- `price_history` - Historical price records with timestamps
- `user_preferences` - Notification preferences (email_enabled, frequency)
- `scraping_stats` - Per-product scraping statistics (success/failure counts)

**Important Relationships:**
- User → Products (one-to-many)
- Product → PriceHistory (one-to-many)
- User → UserPreferences (one-to-one)
- Product → ScrapingStats (one-to-one)

## Development Commands

### Docker (Recommended)

```bash
# Start all services (backend, frontend, db, redis, celery workers)
docker-compose up -d

# View logs
docker-compose logs -f backend          # Backend API logs
docker-compose logs -f celery_worker    # Celery worker logs
docker-compose logs -f frontend         # Frontend logs

# Restart specific services (required after code changes)
docker-compose restart backend celery_worker celery_beat

# Stop all services
docker-compose down

# Rebuild after dependency changes
docker-compose build

# Access container shell
docker-compose exec backend bash
docker-compose exec frontend sh

# Database admin interfaces
# pgAdmin: http://localhost:5050 (admin@pricewatch.com / admin)
# Redis Commander: http://localhost:8081
```

### Backend Development

```bash
cd Backend

# Run tests
pytest                                           # All tests
pytest tests/test_unit_*.py                     # Only unit tests
pytest tests/test_price_decimal_parsing.py      # Specific test file
pytest -v -m scraper                            # Tests with 'scraper' marker
pytest -v -m "not slow"                         # Exclude slow tests

# Code formatting and linting
docker-compose exec -T backend python3 -m black app/ tests/     # Format code
docker-compose exec -T backend python3 -m isort app/ tests/     # Sort imports
docker-compose exec backend flake8 app/ tests/                   # Lint (used in CI)
docker-compose exec backend mypy app/                            # Type checking

# Run single test with verbose output
pytest tests/test_unit_scraper.py::TestPriceScraper::test_amazon_decimal_with_comma -v

# Database migrations (when schema changes)
# Note: Currently using Base.metadata.create_all() - migrations not yet implemented
```

### Frontend Development

```bash
cd Frontend/app

# Development server (with hot reload)
npm run dev                    # Runs on http://localhost:5173

# Build for production
npm run build

# Linting and formatting
npm run lint                   # Check for lint errors
npm run lint:fix              # Auto-fix lint errors
npm run format                # Format code with Prettier
npm run format:check          # Check formatting without changes
npm run type-check            # TypeScript type checking

# Preview production build
npm run preview
```

### Access Points

- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **Frontend**: http://localhost:5173

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`) triggers on pushes and PRs to main/master/develop when Backend/ or Frontend/ files change.

**Backend pipeline**: lint (Black, isort, flake8, mypy) → unit tests with coverage → Docker build → security scan (safety, bandit). Integration tests run only on main/master merges.

**Frontend pipeline**: lint (Prettier, ESLint, TypeScript) → production build → Docker build.

**Deploy**: Auto-deploys to VPS via SSH on main/master after all checks pass. Only rebuilds/restarts services that changed.

## Important Implementation Details

### Price Parsing - Decimal Handling

**Critical**: French e-commerce sites use comma as decimal separator (14,34 €). Both scrapers use regex pattern `r"(\d+)[.,](\d+)"` to capture integer and decimal parts separately, then construct: `float(f"{integer_part}.{decimal_part}")`.

**Scraper Priority**:
1. Try HTTP scraper with BeautifulSoup (fast, low resource)
2. If fails, fallback to Playwright scraper (slow, bypasses anti-bot)
3. Track failures in ScrapingStats to inform user

**Amazon Specifics**:
- Prioritize `.a-price .a-offscreen` selector (most reliable, contains full price)
- Remove newlines from price text: `.replace("\n", "")`
- Amazon may show CAPTCHA randomly - this is a known limitation

### Authentication & Security

- JWT tokens with refresh token rotation
- Rate limiting on sensitive endpoints (login, register, password reset)
- Email verification flow with expiring tokens
- Password strength requirements enforced in backend
- CORS configured for frontend origins

### Background Task System

Celery Beat scheduler runs periodic tasks:
- `check_prices_by_frequency` - Checks products based on individual check_frequency settings
- Products can have different frequencies: daily, hourly, 6h, 12h
- Parallel scraping for improved performance using ThreadPoolExecutor
- Automatic email notifications when price <= target_price

### Error Monitoring

Sentry integration is configured but optional:
- Set `SENTRY_DSN` in `.env` to enable
- Captures errors from FastAPI, Celery, SQLAlchemy, and Redis
- Environment-specific tracking (development/staging/production)

## Code Style

### Python (Backend)
- **Formatter**: Black (line length: 120)
- **Import sorting**: isort (profile: black)
- **Type hints**: Required for public functions
- **Docstrings**: Google style preferred
- Configuration in `pyproject.toml`

### TypeScript (Frontend)
- **Formatter**: Prettier
- **Linter**: ESLint with TypeScript rules
- **Style**: React Hooks, functional components
- Use `clsx` and `tailwind-merge` (tw function) for conditional classes

## Testing Strategy

### Test Markers (pytest)
- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.scraper` - Scraper-related tests
- `@pytest.mark.slow` - Long-running tests
- `@pytest.mark.email` - Email service tests
- `@pytest.mark.celery` - Celery task tests
- `@pytest.mark.admin` - Admin functionality tests

### Critical Test Files
- `tests/test_price_decimal_parsing.py` - Validates decimal price parsing across all scrapers
- `tests/test_unit_scraper.py` - Scraper functionality for all supported sites
- `tests/test_unit_celery_tasks.py` - Background task logic
- `tests/test_unit_check_frequency.py` - Frequency-based price checking

## Configuration

### Environment Variables (Backend)

Required in `Backend/.env`:
```env
DATABASE_URL=postgresql://pricewatch:pricewatch@db:5432/pricewatch
REDIS_URL=redis://redis:6379/0
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(32))">
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your.email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=noreply@pricewatch.com
```

Optional:
```env
SENTRY_DSN=<your-sentry-dsn>
SENTRY_ENVIRONMENT=development
LOG_LEVEL=INFO
ENABLE_JSON_LOGS=false
```

### Environment Variables (Frontend)

In `Frontend/app/.env`:
```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Common Tasks

### Adding a New E-commerce Site

1. Add scraper method in `app/services/scraper.py` (e.g., `_scrape_newsite`)
2. Add corresponding Playwright method in `app/services/playwright_scraper.py`
3. Update site detection logic in both `scrape_product` methods
4. Add tests in `tests/test_price_decimal_parsing.py`
5. Ensure decimal parsing follows the pattern: `r"(\d+)[.,](\d+)"`

### Modifying Database Schema

1. Update SQLAlchemy model in `app/models/`
2. Update corresponding Pydantic schema in `app/schemas/`
3. Currently: Restart services (auto-creates tables via `Base.metadata.create_all()`)
4. TODO: Implement Alembic migrations for production

### Adding New API Endpoint

1. Define route in appropriate endpoint file (`app/api/endpoints/`)
2. Add Pydantic schemas in `app/schemas/` for request/response validation
3. Implement business logic in service layer (`app/services/`)
4. Add authentication dependency if needed: `current_user: User = Depends(get_current_user)`
5. Add rate limiting if needed: `Depends(rate_limiter("endpoint_name", max_requests=10, window=60))`
6. Write unit tests in `tests/test_unit_*.py`
7. Update API documentation strings (auto-generated in Swagger)

## Troubleshooting

### Price Scraping Returns Wrong Decimals
- Verify regex pattern includes both integer and decimal capture groups
- Check for newlines in price text (`.replace("\n", "")`)
- Inspect actual HTML with browser DevTools
- Test with `tests/test_price_decimal_parsing.py`

### Celery Tasks Not Running
- Verify Redis is running: `docker-compose ps redis`
- Check Celery worker logs: `docker-compose logs -f celery_worker`
- Ensure task is registered in `tasks.py` with `@celery_app.task(name="task_name")`
- Verify Celery Beat is running: `docker-compose logs -f celery_beat`

### Database Connection Errors
- Ensure PostgreSQL is healthy: `docker-compose ps db`
- Check DATABASE_URL format in `.env`
- Wait for database to be ready before starting backend (healthcheck configured in docker-compose)

### Frontend API Calls Failing
- Verify CORS origins in `app/main.py` include frontend URL
- Check VITE_API_URL in frontend `.env`
- Verify backend is running: http://localhost:8000/health
- Check browser console for specific error messages
