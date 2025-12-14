"""
i18n utility functions for FastAPI.
"""
import os
import gettext
from datetime import datetime
from typing import Optional
from babel import Locale, dates, numbers, UnknownLocaleError
from fastapi import Request, Response

from config import settings


def get_translator(locale: str = None) -> gettext.GNUTranslations:
    """
    Get a translator instance for the specified locale.
    
    Args:
        locale: Locale code (e.g., 'en', 'es', 'he'). Defaults to settings.default_locale.
    
    Returns:
        GNUTranslations instance for the locale.
    """
    if locale is None:
        locale = settings.default_locale
    
    # Validate locale
    if locale not in settings.supported_locales:
        locale = settings.default_locale
    
    # Get the locale directory path
    locale_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), settings.locale_dir)
    locale_path = os.path.join(locale_dir, locale, "LC_MESSAGES")
    
    try:
        translation = gettext.translation("messages", locale_path, languages=[locale])
        return translation
    except FileNotFoundError:
        # Fallback to default locale if translation file not found
        if locale != settings.default_locale:
            default_path = os.path.join(locale_dir, settings.default_locale, "LC_MESSAGES")
            try:
                return gettext.translation("messages", default_path, languages=[settings.default_locale])
            except FileNotFoundError:
                return gettext.NullTranslations()
        return gettext.NullTranslations()


def get_locale_from_accept_language(accept_language: Optional[str]) -> str:
    """
    Extract the preferred locale from the Accept-Language header.
    
    Args:
        accept_language: Accept-Language header value (e.g., 'en-US,en;q=0.9,es;q=0.8').
    
    Returns:
        Locale code (e.g., 'en', 'es', 'he').
    """
    if not accept_language:
        return settings.default_locale
    
    # Parse Accept-Language header
    # Format: "en-US,en;q=0.9,es;q=0.8"
    languages = []
    for lang_part in accept_language.split(","):
        lang_part = lang_part.strip()
        if ";" in lang_part:
            lang, q = lang_part.split(";")
            q_value = float(q.split("=")[1])
        else:
            lang = lang_part
            q_value = 1.0
        
        # Extract base language code (e.g., 'en' from 'en-US')
        base_lang = lang.split("-")[0].lower()
        languages.append((base_lang, q_value))
    
    # Sort by quality value (descending)
    languages.sort(key=lambda x: x[1], reverse=True)
    
    # Find the first supported locale
    for lang, _ in languages:
        if lang in settings.supported_locales:
            return lang
    
    return settings.default_locale


def format_datetime(dt: datetime, locale: str = None, format_type: str = "medium") -> str:
    """
    Format a datetime object according to the specified locale.
    
    Args:
        dt: Datetime object to format.
        locale: Locale code. Defaults to settings.default_locale.
        format_type: Format type ('short', 'medium', 'long', 'full').
    
    Returns:
        Formatted datetime string.
    """
    if locale is None:
        locale = settings.default_locale
    
    try:
        locale_obj = Locale.parse(locale)
    except (UnknownLocaleError, ValueError):
        locale_obj = Locale.parse(settings.default_locale)
    
    return dates.format_datetime(dt, format=format_type, locale=locale_obj)


def format_currency(amount: float, locale: str = None, currency: str = "USD") -> str:
    """
    Format a number as currency according to the specified locale.
    
    Args:
        amount: Amount to format.
        locale: Locale code. Defaults to settings.default_locale.
        currency: Currency code (e.g., 'USD', 'EUR', 'ILS').
    
    Returns:
        Formatted currency string.
    """
    if locale is None:
        locale = settings.default_locale
    
    try:
        locale_obj = Locale.parse(locale)
    except (UnknownLocaleError, ValueError):
        locale_obj = Locale.parse(settings.default_locale)
    
    return numbers.format_currency(amount, currency, locale=locale_obj)


def store_locale(response: Response, locale: str) -> None:
    """
    Store the user's preferred locale in a cookie.
    
    Args:
        response: FastAPI Response object.
        locale: Locale code to store.
    """
    if locale in settings.supported_locales:
        response.set_cookie(
            key="locale",
            value=locale,
            max_age=365 * 24 * 60 * 60,  # 1 year
            httponly=True,
            samesite="lax"
        )


def get_stored_locale(request: Request) -> Optional[str]:
    """
    Get the user's stored locale from cookies.
    
    Args:
        request: FastAPI Request object.
    
    Returns:
        Locale code if found, None otherwise.
    """
    locale = request.cookies.get("locale")
    if locale and locale in settings.supported_locales:
        return locale
    return None

