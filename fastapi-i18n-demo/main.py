"""
FastAPI i18n Demo Application

This application demonstrates internationalization (i18n) support in FastAPI,
including translations, pluralization, datetime localization, currency formatting,
and automatic locale detection.
"""
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Request, Response, Query
from fastapi.responses import JSONResponse

from config import settings
from i18n.utils import (
    get_translator,
    get_locale_from_accept_language,
    format_datetime,
    format_currency,
    store_locale,
    get_stored_locale,
)

app = FastAPI(title=settings.app_name, version="1.0.0")


def get_locale(request: Request) -> str:
    """
    Determine the user's preferred locale from:
    1. Query parameter (?locale=es)
    2. Cookie (stored preference)
    3. Accept-Language header
    4. Default locale
    
    Args:
        request: FastAPI Request object.
    
    Returns:
        Locale code.
    """
    # Check query parameter first
    locale = request.query_params.get("locale")
    if locale and locale in settings.supported_locales:
        return locale
    
    # Check cookie
    stored_locale = get_stored_locale(request)
    if stored_locale:
        return stored_locale
    
    # Check Accept-Language header
    accept_language = request.headers.get("Accept-Language")
    if accept_language:
        return get_locale_from_accept_language(accept_language)
    
    # Default
    return settings.default_locale


@app.get("/")
async def root(request: Request, response: Response, locale: Optional[str] = Query(None)):
    """
    Root endpoint with basic translation support.
    
    Supports locale via:
    - Query parameter: ?locale=en
    - Cookie (stored preference)
    - Accept-Language header
    """
    # Get locale
    user_locale = locale if locale and locale in settings.supported_locales else get_locale(request)
    
    # Store locale in cookie if provided via query parameter
    if locale and locale in settings.supported_locales:
        store_locale(response, locale)
    
    # Get translator
    translator = get_translator(user_locale)
    _ = translator.gettext
    
    return {
        "message": _("Welcome to FastAPI i18n Demo"),
        "locale": user_locale,
        "supported_locales": settings.supported_locales,
    }


@app.get("/hello/{name}")
async def hello(
    name: str,
    request: Request,
    locale: Optional[str] = Query(None)
):
    """
    Personalized greeting endpoint with translation.
    
    Example: /hello/John?locale=es
    """
    user_locale = locale if locale and locale in settings.supported_locales else get_locale(request)
    translator = get_translator(user_locale)
    _ = translator.gettext
    
    return {
        "message": _("Hello, {name}!").format(name=name),
        "locale": user_locale,
    }


@app.get("/plural")
async def plural(
    request: Request,
    count: int = Query(1, ge=0),
    locale: Optional[str] = Query(None)
):
    """
    Pluralization example endpoint.
    
    Example: /plural?count=5&locale=es
    """
    user_locale = locale if locale and locale in settings.supported_locales else get_locale(request)
    translator = get_translator(user_locale)
    ngettext = translator.ngettext
    
    return {
        "message": ngettext(
            "You have {count} item",
            "You have {count} items",
            count
        ).format(count=count),
        "count": count,
        "locale": user_locale,
    }


@app.get("/datetime")
async def datetime_endpoint(
    request: Request,
    locale: Optional[str] = Query(None),
    format_type: str = Query("medium", regex="^(short|medium|long|full)$")
):
    """
    Datetime localization endpoint.
    
    Example: /datetime?locale=es&format_type=long
    """
    user_locale = locale if locale and locale in settings.supported_locales else get_locale(request)
    translator = get_translator(user_locale)
    _ = translator.gettext
    
    now = datetime.now()
    formatted_dt = format_datetime(now, locale=user_locale, format_type=format_type)
    
    return {
        "message": _("Current datetime"),
        "datetime": formatted_dt,
        "iso_datetime": now.isoformat(),
        "locale": user_locale,
        "format_type": format_type,
    }


@app.get("/currency")
async def currency_endpoint(
    request: Request,
    amount: float = Query(100.50),
    currency: str = Query("USD"),
    locale: Optional[str] = Query(None)
):
    """
    Currency formatting endpoint.
    
    Example: /currency?amount=1234.56&currency=EUR&locale=es
    """
    user_locale = locale if locale and locale in settings.supported_locales else get_locale(request)
    translator = get_translator(user_locale)
    _ = translator.gettext
    
    formatted_currency = format_currency(amount, locale=user_locale, currency=currency)
    
    return {
        "message": _("Currency example"),
        "amount": amount,
        "currency": currency,
        "formatted": formatted_currency,
        "locale": user_locale,
    }


@app.post("/locale")
async def set_locale(
    locale: str = Query(..., regex="^(en|es|he)$"),
    response: Response = None
):
    """
    Set the user's preferred locale and store it in a cookie.
    
    Example: POST /locale?locale=es
    """
    if locale not in settings.supported_locales:
        return JSONResponse(
            status_code=400,
            content={"error": f"Unsupported locale. Supported: {settings.supported_locales}"}
        )
    
    translator = get_translator(locale)
    _ = translator.gettext
    
    store_locale(response, locale)
    
    return {
        "message": _("Language changed successfully"),
        "locale": locale,
    }


@app.get("/info")
async def info():
    """
    Get information about supported locales and features.
    """
    return {
        "supported_locales": settings.supported_locales,
        "default_locale": settings.default_locale,
        "features": [
            "Basic translations",
            "Pluralization",
            "Datetime localization",
            "Currency formatting",
            "Automatic locale detection",
            "Locale persistence via cookies",
            "RTL language support (Hebrew)",
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

