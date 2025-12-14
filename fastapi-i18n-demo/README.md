# FastAPI i18n Demo

A comprehensive FastAPI application demonstrating internationalization (i18n) support with translations, pluralization, datetime localization, currency formatting, and automatic locale detection.

## Features

- ✅ **Basic Translations** - Support for multiple languages (English, Spanish, Hebrew)
- ✅ **Pluralization** - Proper handling of singular/plural forms
- ✅ **Datetime Localization** - Locale-aware date and time formatting
- ✅ **Currency Formatting** - Localized currency display
- ✅ **Automatic Locale Detection** - Detects user's preferred language from:
  - Query parameters (`?locale=es`)
  - Cookies (stored preferences)
  - Accept-Language header
- ✅ **Locale Persistence** - Stores user preferences in cookies
- ✅ **RTL Language Support** - Full support for right-to-left languages (Hebrew)

## Prerequisites

- Python 3.13+
- [UV](https://github.com/astral-sh/uv) package manager

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd fastapi-i18n-demo
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Compile translation files:**
   ```bash
   uv run python compile_translations.py
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
  "supported_locales": ["en", "es", "he"],
  "default_locale": "en",
  "features": [
    "Basic translations",
    "Pluralization",
    "Datetime localization",
    "Currency formatting",
    "Automatic locale detection",
    "Locale persistence via cookies",
    "RTL language support (Hebrew)"
  ]
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
├── compile_translations.py # Script to compile .po to .mo files
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
│   └── he/
│       └── LC_MESSAGES/
│           ├── messages.po # Hebrew translations (source)
│           └── messages.mo # Hebrew translations (compiled)
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
```

## Dependencies

- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation and settings
- **Babel** - Internationalization library
  - Translation support (gettext)
  - Datetime formatting
  - Currency formatting
  - Locale parsing

## How It Works

1. **Translation System**: Uses Python's `gettext` module with Babel for managing translation files (`.po` and `.mo`)

2. **Locale Detection**: The `get_locale()` function checks multiple sources to determine the user's preferred language

3. **Pluralization**: Uses `ngettext()` to handle singular/plural forms based on locale-specific rules

4. **Formatting**: Babel's `dates` and `numbers` modules provide locale-aware formatting for datetimes and currencies

5. **Persistence**: Cookies store the user's language preference for future visits

## Further Reading

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Babel Documentation](https://babel.pocoo.org/)
- [Python gettext Documentation](https://docs.python.org/3/library/gettext.html)
- [ISO 639 Language Codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)

## License

This project is provided as a demonstration and learning resource.

