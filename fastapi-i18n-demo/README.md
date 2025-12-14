# FastAPI i18n Demo

A comprehensive FastAPI application demonstrating internationalization (i18n) support with translations, pluralization, datetime localization, currency formatting, and automatic locale detection.

## Features

- ✅ **Basic Translations** - Support for multiple languages (English, Spanish, Hebrew, Uzbek, Russian)
- ✅ **Pluralization** - Proper handling of singular/plural forms
- ✅ **Datetime Localization** - Locale-aware date and time formatting
- ✅ **Currency Formatting** - Localized currency display
- ✅ **Automatic Locale Detection** - Detects user's preferred language from:
  - Query parameters (`?locale=es`)
  - Cookies (stored preferences)
  - Accept-Language header
- ✅ **Locale Persistence** - Stores user preferences in cookies
- ✅ **RTL Language Support** - Full support for right-to-left languages (Hebrew)
- ✅ **Database Models with Translatable Fields** - Category and Article models with multi-language support
- ✅ **RESTful API** - Complete CRUD endpoints for categories and articles with automatic translation

## Prerequisites

- Python 3.13+
- [UV](https://github.com/astral-sh/uv) package manager
- PostgreSQL 12+ (for database)

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd fastapi-i18n-demo
   ```

2. **Set up PostgreSQL database:**
   ```bash
   # Create database (using psql)
   createdb fastapi_i18n
   
   # Or using SQL
   psql -U postgres -c "CREATE DATABASE fastapi_i18n;"
   ```

3. **Configure database connection:**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env file with your PostgreSQL credentials
   # DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_i18n
   ```

4. **Install dependencies:**
   ```bash
   uv sync
   ```

5. **Compile translation files:**
   ```bash
   uv run python compile_translations.py
   ```

6. **Run database migrations:**
   ```bash
   # Apply migrations to create tables
   uv run alembic upgrade head
   ```

7. **Initialize database with sample data:**
   ```bash
   uv run python init_db.py
   ```

## Running the Application

Start the FastAPI server:

```bash
uv run uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

Interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### 1. Root Endpoint - Basic Translation

**GET** `/`

Returns a welcome message in the user's preferred language.

**Examples:**
```bash
# Using query parameter
curl http://localhost:8000/?locale=es

# Using Accept-Language header
curl -H "Accept-Language: es" http://localhost:8000/

# Using cookie (after setting locale)
curl -b "locale=he" http://localhost:8000/
```

**Response:**
```json
{
  "message": "Welcome to FastAPI i18n Demo",
  "locale": "en",
  "supported_locales": ["en", "es", "he"]
}
```

### 2. Personalized Greeting

**GET** `/hello/{name}`

Returns a personalized greeting in the user's preferred language.

**Examples:**
```bash
curl http://localhost:8000/hello/John?locale=es
curl http://localhost:8000/hello/María?locale=he
```

**Response:**
```json
{
  "message": "¡Hola, John!",
  "locale": "es"
}
```

### 3. Pluralization

**GET** `/plural?count={number}`

Demonstrates proper pluralization handling.

**Examples:**
```bash
curl http://localhost:8000/plural?count=1&locale=es
curl http://localhost:8000/plural?count=5&locale=es
curl http://localhost:8000/plural?count=0&locale=he
```

**Response (count=1):**
```json
{
  "message": "Tienes 1 artículo",
  "count": 1,
  "locale": "es"
}
```

**Response (count=5):**
```json
{
  "message": "Tienes 5 artículos",
  "count": 5,
  "locale": "es"
}
```

### 4. Datetime Localization

**GET** `/datetime?format_type={short|medium|long|full}`

Returns the current datetime formatted according to the locale.

**Examples:**
```bash
curl http://localhost:8000/datetime?locale=es&format_type=long
curl http://localhost:8000/datetime?locale=he&format_type=full
```

**Response:**
```json
{
  "message": "Fecha y hora actual",
  "datetime": "15 de enero de 2024, 14:30:00",
  "iso_datetime": "2024-01-15T14:30:00",
  "locale": "es",
  "format_type": "long"
}
```

### 5. Currency Formatting

**GET** `/currency?amount={number}&currency={CODE}`

Formats a number as currency according to the locale.

**Examples:**
```bash
curl http://localhost:8000/currency?amount=1234.56&currency=USD&locale=es
curl http://localhost:8000/currency?amount=1000&currency=EUR&locale=he
curl http://localhost:8000/currency?amount=500&currency=ILS&locale=he
```

**Response:**
```json
{
  "message": "Ejemplo de moneda",
  "amount": 1234.56,
  "currency": "USD",
  "formatted": "1.234,56 $",
  "locale": "es"
}
```

### 6. Set Locale

**POST** `/locale?locale={en|es|he}`

Sets the user's preferred locale and stores it in a cookie.

**Examples:**
```bash
curl -X POST http://localhost:8000/locale?locale=es
curl -X POST http://localhost:8000/locale?locale=he
```

**Response:**
```json
{
  "message": "Language changed successfully",
  "locale": "es"
}
```

### 7. API Information

**GET** `/info`

Returns information about supported locales and features.

**Example:**
```bash
curl http://localhost:8000/info
```

**Response:**
```json
{
  "supported_locales": ["en", "es", "he", "uz", "ru"],
  "default_locale": "en",
  "features": [
    "Basic translations",
    "Pluralization",
    "Datetime localization",
    "Currency formatting",
    "Automatic locale detection",
    "Locale persistence via cookies",
    "RTL language support (Hebrew)",
    "Database models with translatable fields"
  ]
}
```

### 8. Get Categories List

**GET** `/categories`

Returns a list of all categories with translated fields based on the user's locale.

**Examples:**
```bash
# Get categories in English (default)
curl http://localhost:8000/categories

# Get categories in Russian
curl http://localhost:8000/categories?locale=ru

# Get categories in Uzbek
curl http://localhost:8000/categories?locale=uz
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "Technology",
    "description": "Articles about technology and innovation",
    "locale": "en"
  },
  {
    "id": 2,
    "title": "Science",
    "description": "Scientific articles and research",
    "locale": "en"
  }
]
```

**Response (Russian):**
```json
[
  {
    "id": 1,
    "title": "Технологии",
    "description": "Статьи о технологиях и инновациях",
    "locale": "ru"
  },
  {
    "id": 2,
    "title": "Наука",
    "description": "Научные статьи и исследования",
    "locale": "ru"
  }
]
```

### 9. Get Category Detail

**GET** `/categories/{category_id}`

Returns a single category with translated fields.

**Examples:**
```bash
curl http://localhost:8000/categories/1?locale=uz
curl http://localhost:8000/categories/1?locale=ru
```

**Response:**
```json
{
  "id": 1,
  "title": "Technology",
  "description": "Articles about technology and innovation",
  "locale": "en",
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:00:00"
}
```

### 10. Get Category with Articles

**GET** `/categories/{category_id}/detail`

Returns a category with all its articles, all with translated fields.

**Examples:**
```bash
curl http://localhost:8000/categories/1/detail?locale=ru
curl http://localhost:8000/categories/1/detail?locale=uz
```

**Response:**
```json
{
  "id": 1,
  "title": "Technology",
  "description": "Articles about technology and innovation",
  "locale": "en",
  "articles": [
    {
      "id": 1,
      "category_id": 1,
      "title": "Introduction to Python",
      "description": "Learn the basics of Python programming language",
      "locale": "en"
    },
    {
      "id": 2,
      "category_id": 1,
      "title": "FastAPI Best Practices",
      "description": "Best practices for building APIs with FastAPI",
      "locale": "en"
    }
  ],
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:00:00"
}
```

### 11. Get Articles List

**GET** `/articles`

Returns a list of all articles with translated fields. Optionally filter by category.

**Examples:**
```bash
# Get all articles
curl http://localhost:8000/articles?locale=ru

# Get articles for a specific category
curl http://localhost:8000/articles?locale=uz&category_id=1
```

**Response:**
```json
[
  {
    "id": 1,
    "category_id": 1,
    "title": "Introduction to Python",
    "description": "Learn the basics of Python programming language",
    "locale": "en"
  },
  {
    "id": 2,
    "category_id": 1,
    "title": "FastAPI Best Practices",
    "description": "Best practices for building APIs with FastAPI",
    "locale": "en"
  }
]
```

**Response (Russian):**
```json
[
  {
    "id": 1,
    "category_id": 1,
    "title": "Введение в Python",
    "description": "Изучите основы языка программирования Python",
    "locale": "ru"
  },
  {
    "id": 2,
    "category_id": 1,
    "title": "Лучшие практики FastAPI",
    "description": "Лучшие практики создания API с FastAPI",
    "locale": "ru"
  }
]
```

### 12. Get Article Detail

**GET** `/articles/{article_id}`

Returns a single article with translated fields.

**Examples:**
```bash
curl http://localhost:8000/articles/1?locale=uz
curl http://localhost:8000/articles/1?locale=ru
```

**Response:**
```json
{
  "id": 1,
  "category_id": 1,
  "title": "Introduction to Python",
  "description": "Learn the basics of Python programming language",
  "locale": "en",
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:00:00"
}
```

## Locale Detection Priority

The application detects the user's preferred locale in the following order:

1. **Query Parameter** - `?locale=es` (highest priority)
2. **Cookie** - Stored preference from previous visits
3. **Accept-Language Header** - Browser language preference
4. **Default Locale** - Falls back to English (`en`)

## Project Structure

```
fastapi-i18n-demo/
├── main.py                 # FastAPI application with all endpoints
├── config.py               # Pydantic settings configuration
├── database.py             # Database connection and session management
├── models.py               # SQLAlchemy models (Category, Article)
├── schemas.py              # Pydantic schemas for API requests/responses
├── compile_translations.py # Script to compile .po to .mo files
├── init_db.py              # Database initialization script
├── i18n/
│   ├── __init__.py         # Module exports
│   └── utils.py            # i18n utility functions
├── locale/
│   ├── en/
│   │   └── LC_MESSAGES/
│   │       ├── messages.po # English translations (source)
│   │       └── messages.mo # English translations (compiled)
│   ├── es/
│   │   └── LC_MESSAGES/
│   │       ├── messages.po # Spanish translations (source)
│   │       └── messages.mo # Spanish translations (compiled)
│   ├── he/
│   │   └── LC_MESSAGES/
│   │       ├── messages.po # Hebrew translations (source)
│   │       └── messages.mo # Hebrew translations (compiled)
│   ├── uz/                 # Uzbek (database translations only)
│   └── ru/                 # Russian (database translations only)
├── app.db                   # SQLite database (created on first run)
├── pyproject.toml          # Project dependencies
└── README.md               # This file
```

## Adding New Translations

1. **Edit the `.po` file** for your language in `locale/{locale}/LC_MESSAGES/messages.po`

2. **Add your translation:**
   ```po
   msgid "Your message"
   msgstr "Tu mensaje"
   ```

3. **For pluralization:**
   ```po
   msgid "You have {count} item"
   msgid_plural "You have {count} items"
   msgstr[0] "Tienes {count} artículo"
   msgstr[1] "Tienes {count} artículos"
   ```

4. **Compile translations:**
   ```bash
   uv run python compile_translations.py
   ```

5. **Add the locale to `config.py`:**
   ```python
   supported_locales: list[str] = ["en", "es", "he", "fr"]  # Add "fr"
   ```

## Configuration

You can customize the application by editing `config.py` or using environment variables:

**Environment Variables:**
```bash
export DEFAULT_LOCALE=es
export SUPPORTED_LOCALES='["en","es","he","fr"]'
```

Or create a `.env` file:
```env
DEFAULT_LOCALE=es
SUPPORTED_LOCALES=["en","es","he","fr"]
```

## Testing Examples

### Test with curl

```bash
# English
curl http://localhost:8000/?locale=en

# Spanish
curl http://localhost:8000/?locale=es

# Hebrew
curl http://localhost:8000/?locale=he

# Pluralization
curl "http://localhost:8000/plural?count=1&locale=es"
curl "http://localhost:8000/plural?count=5&locale=es"

# Datetime
curl "http://localhost:8000/datetime?locale=es&format_type=long"

# Currency
curl "http://localhost:8000/currency?amount=1234.56&currency=USD&locale=es"
```

### Test with Python requests

```python
import requests

# Test basic translation
response = requests.get("http://localhost:8000/?locale=es")
print(response.json())

# Test pluralization
response = requests.get("http://localhost:8000/plural?count=5&locale=es")
print(response.json())

# Test with Accept-Language header
headers = {"Accept-Language": "es,en;q=0.9"}
response = requests.get("http://localhost:8000/", headers=headers)
print(response.json())

# Test database endpoints
# Get categories in Russian
response = requests.get("http://localhost:8000/categories?locale=ru")
print(response.json())

# Get articles in Uzbek
response = requests.get("http://localhost:8000/articles?locale=uz")
print(response.json())

# Get category with articles in Russian
response = requests.get("http://localhost:8000/categories/1/detail?locale=ru")
print(response.json())
```

## Database Models

The application includes two main models with translatable fields:

### Category Model
- `id` - Primary key
- `title_en`, `title_ru`, `title_uz`, `title_es`, `title_he` - Translatable title fields
- `description_en`, `description_ru`, `description_uz`, `description_es`, `description_he` - Translatable description fields
- `created_at`, `updated_at` - Timestamps
- `articles` - Relationship to Article model

### Article Model
- `id` - Primary key
- `category_id` - Foreign key to Category
- `title_en`, `title_ru`, `title_uz`, `title_es`, `title_he` - Translatable title fields
- `description_en`, `description_ru`, `description_uz`, `description_es`, `description_he` - Translatable description fields
- `created_at`, `updated_at` - Timestamps
- `category` - Relationship to Category model

Both models include helper methods:
- `get_title(locale)` - Returns title in specified locale, falls back to English
- `get_description(locale)` - Returns description in specified locale, falls back to English

## Dependencies

- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation and settings
- **SQLAlchemy** - SQL toolkit and ORM (async support)
- **asyncpg** - Fast PostgreSQL async driver
- **Alembic** - Database migration tool
- **Babel** - Internationalization library
  - Translation support (gettext)
  - Datetime formatting
  - Currency formatting
  - Locale parsing

## Database

The application uses **PostgreSQL** with **asyncpg** for async database operations. All database operations are fully asynchronous for better performance.

### Database Configuration

The database connection is configured via the `DATABASE_URL` environment variable:

```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_i18n
```

### Async Database Operations

All database queries use SQLAlchemy's async API:
- `AsyncSession` for database sessions
- `select()` statements for queries
- `await` for all database operations
- Proper connection pooling with asyncpg

## How It Works

1. **Translation System**: 
   - Uses Python's `gettext` module with Babel for managing translation files (`.po` and `.mo`)
   - Database models store translations in separate columns (e.g., `title_en`, `title_ru`, `title_uz`)

2. **Async Database**: 
   - Uses PostgreSQL with asyncpg for high-performance async database operations
   - All database queries are asynchronous using SQLAlchemy's async API
   - Proper connection pooling and resource management

3. **Lifespan Management**: 
   - Uses FastAPI's modern `lifespan` context manager instead of deprecated `@app.on_event()`
   - Handles database initialization on startup and cleanup on shutdown

4. **Locale Detection**: The `get_locale()` function checks multiple sources to determine the user's preferred language

5. **Database Translations**: Models include `get_title()` and `get_description()` methods that automatically return the appropriate translation based on the user's locale, with fallback to English

6. **Pluralization**: Uses `ngettext()` to handle singular/plural forms based on locale-specific rules

7. **Formatting**: Babel's `dates` and `numbers` modules provide locale-aware formatting for datetimes and currencies

8. **Persistence**: Cookies store the user's language preference for future visits

## Database Migrations with Alembic

The project uses Alembic for database migrations. All migration files are located in the `alembic/versions/` directory.

### Migration Files

- **`alembic.ini`** - Alembic configuration file
- **`alembic/env.py`** - Alembic environment configuration (configured for async PostgreSQL)
- **`alembic/versions/`** - Directory containing migration files

### Common Alembic Commands

```bash
# Create a new migration (auto-generate from model changes)
uv run alembic revision --autogenerate -m "Description of changes"

# Create a new empty migration
uv run alembic revision -m "Description of changes"

# Apply all pending migrations
uv run alembic upgrade head

# Apply migrations up to a specific revision
uv run alembic upgrade <revision_id>

# Rollback one migration
uv run alembic downgrade -1

# Rollback to a specific revision
uv run alembic downgrade <revision_id>

# Show current migration status
uv run alembic current

# Show migration history
uv run alembic history

# Show pending migrations
uv run alembic heads
```

### Initial Migration

The initial migration (`ef546f274885_initial_migration_create_categories_and_.py`) creates:
- `categories` table with translatable fields
- `articles` table with translatable fields and foreign key to categories

### Migration Workflow

1. **Make changes to models** in `models.py`
2. **Generate migration:**
   ```bash
   uv run alembic revision --autogenerate -m "Your migration message"
   ```
3. **Review the generated migration** in `alembic/versions/`
4. **Apply the migration:**
   ```bash
   uv run alembic upgrade head
   ```

### Note on Async Database

Alembic migrations run in **sync mode** (required by Alembic), but the configuration automatically converts the async database URL (`postgresql+asyncpg://`) to a sync URL (`postgresql://`) for migrations. The application itself uses async operations at runtime.

## Further Reading

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Babel Documentation](https://babel.pocoo.org/)
- [Python gettext Documentation](https://docs.python.org/3/library/gettext.html)
- [ISO 639 Language Codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)

## License

This project is provided as a demonstration and learning resource.

