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

from sqlalchemy.orm import Session
from fastapi import Depends

from config import settings
from database import get_db, init_db
from models import Category, Article
from schemas import (
    CategoryResponse,
    CategoryListResponse,
    CategoryWithArticlesResponse,
    ArticleResponse,
    ArticleListResponse,
)
from i18n.utils import (
    get_translator,
    get_locale_from_accept_language,
    format_datetime,
    format_currency,
    store_locale,
    get_stored_locale,
)

app = FastAPI(title=settings.app_name, version="1.0.0")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


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
            "Database models with translatable fields",
        ],
    }


# ============================================================================
# Category API Endpoints
# ============================================================================

@app.get("/categories", response_model=list[CategoryListResponse])
async def get_categories(
    request: Request,
    locale: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get list of all categories with translated fields.
    
    Example: /categories?locale=ru
    """
    user_locale = locale if locale and locale in settings.supported_locales else get_locale(request)
    
    # Get all categories from database
    categories = db.query(Category).all()
    
    # Build response with translated fields
    result = []
    for category in categories:
        result.append(CategoryListResponse(
            id=category.id,
            title=category.get_title(user_locale),
            description=category.get_description(user_locale),
            locale=user_locale
        ))
    
    return result


@app.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    request: Request,
    locale: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get a single category by ID with translated fields.
    
    Example: /categories/1?locale=uz
    """
    user_locale = locale if locale and locale in settings.supported_locales else get_locale(request)
    
    # Get category from database
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        return JSONResponse(
            status_code=404,
            content={"error": f"Category with id {category_id} not found"}
        )
    
    return CategoryResponse(
        id=category.id,
        title=category.get_title(user_locale),
        description=category.get_description(user_locale),
        locale=user_locale,
        created_at=category.created_at,
        updated_at=category.updated_at
    )


@app.get("/categories/{category_id}/detail", response_model=CategoryWithArticlesResponse)
async def get_category_with_articles(
    category_id: int,
    request: Request,
    locale: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get a category with all its articles, with translated fields.
    
    Example: /categories/1/detail?locale=ru
    """
    user_locale = locale if locale and locale in settings.supported_locales else get_locale(request)
    
    # Get category with articles from database
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        return JSONResponse(
            status_code=404,
            content={"error": f"Category with id {category_id} not found"}
        )
    
    # Build articles list with translated fields
    articles = []
    for article in category.articles:
        articles.append(ArticleListResponse(
            id=article.id,
            category_id=article.category_id,
            title=article.get_title(user_locale),
            description=article.get_description(user_locale),
            locale=user_locale
        ))
    
    return CategoryWithArticlesResponse(
        id=category.id,
        title=category.get_title(user_locale),
        description=category.get_description(user_locale),
        locale=user_locale,
        articles=articles,
        created_at=category.created_at,
        updated_at=category.updated_at
    )


# ============================================================================
# Article API Endpoints
# ============================================================================

@app.get("/articles", response_model=list[ArticleListResponse])
async def get_articles(
    request: Request,
    locale: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get list of all articles with translated fields.
    Optionally filter by category_id.
    
    Example: /articles?locale=uz&category_id=1
    """
    user_locale = locale if locale and locale in settings.supported_locales else get_locale(request)
    
    # Build query
    query = db.query(Article)
    if category_id is not None:
        query = query.filter(Article.category_id == category_id)
    
    # Get articles from database
    articles = query.all()
    
    # Build response with translated fields
    result = []
    for article in articles:
        result.append(ArticleListResponse(
            id=article.id,
            category_id=article.category_id,
            title=article.get_title(user_locale),
            description=article.get_description(user_locale),
            locale=user_locale
        ))
    
    return result


@app.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    request: Request,
    locale: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get a single article by ID with translated fields.
    
    Example: /articles/1?locale=ru
    """
    user_locale = locale if locale and locale in settings.supported_locales else get_locale(request)
    
    # Get article from database
    article = db.query(Article).filter(Article.id == article_id).first()
    
    if not article:
        return JSONResponse(
            status_code=404,
            content={"error": f"Article with id {article_id} not found"}
        )
    
    return ArticleResponse(
        id=article.id,
        category_id=article.category_id,
        title=article.get_title(user_locale),
        description=article.get_description(user_locale),
        locale=user_locale,
        created_at=article.created_at,
        updated_at=article.updated_at
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

