"""
Example usage script for FastAPI i18n Demo.

This script demonstrates how to use the API endpoints programmatically.
Run the FastAPI server first: uv run uvicorn main:app --reload
"""
import requests

BASE_URL = "http://localhost:8000"


def test_basic_translation():
    """Test basic translation with different locales."""
    print("\n=== Testing Basic Translation ===")
    
    for locale in ["en", "es", "he"]:
        response = requests.get(f"{BASE_URL}/?locale={locale}")
        data = response.json()
        print(f"Locale {locale}: {data['message']}")


def test_hello():
    """Test personalized greeting."""
    print("\n=== Testing Hello Endpoint ===")
    
    response = requests.get(f"{BASE_URL}/hello/John?locale=es")
    data = response.json()
    print(f"Spanish: {data['message']}")
    
    response = requests.get(f"{BASE_URL}/hello/מריה?locale=he")
    data = response.json()
    print(f"Hebrew: {data['message']}")


def test_pluralization():
    """Test pluralization."""
    print("\n=== Testing Pluralization ===")
    
    for count in [0, 1, 2, 5]:
        response = requests.get(f"{BASE_URL}/plural?count={count}&locale=es")
        data = response.json()
        print(f"Count {count}: {data['message']}")


def test_datetime():
    """Test datetime localization."""
    print("\n=== Testing Datetime Localization ===")
    
    for locale in ["en", "es", "he"]:
        response = requests.get(f"{BASE_URL}/datetime?locale={locale}&format_type=long")
        data = response.json()
        print(f"Locale {locale}: {data['datetime']}")


def test_currency():
    """Test currency formatting."""
    print("\n=== Testing Currency Formatting ===")
    
    test_cases = [
        ("en", "USD", 1234.56),
        ("es", "EUR", 1234.56),
        ("he", "ILS", 1000),
    ]
    
    for locale, currency, amount in test_cases:
        response = requests.get(
            f"{BASE_URL}/currency?amount={amount}&currency={currency}&locale={locale}"
        )
        data = response.json()
        print(f"Locale {locale}, {currency}: {data['formatted']}")


def test_locale_detection():
    """Test automatic locale detection from Accept-Language header."""
    print("\n=== Testing Locale Detection ===")
    
    headers = {"Accept-Language": "es,en;q=0.9"}
    response = requests.get(f"{BASE_URL}/", headers=headers)
    data = response.json()
    print(f"Detected locale: {data['locale']}")
    print(f"Message: {data['message']}")


def test_set_locale():
    """Test setting locale via POST."""
    print("\n=== Testing Set Locale ===")
    
    response = requests.post(f"{BASE_URL}/locale?locale=es")
    data = response.json()
    print(f"Response: {data['message']}")
    
    # Now use the cookie
    cookies = response.cookies
    response = requests.get(f"{BASE_URL}/", cookies=cookies)
    data = response.json()
    print(f"Using cookie, locale: {data['locale']}")


if __name__ == "__main__":
    print("FastAPI i18n Demo - Example Usage")
    print("=" * 50)
    print("\nMake sure the server is running:")
    print("  uv run uvicorn main:app --reload")
    print("\nPress Enter to continue...")
    input()
    
    try:
        test_basic_translation()
        test_hello()
        test_pluralization()
        test_datetime()
        test_currency()
        test_locale_detection()
        test_set_locale()
        
        print("\n" + "=" * 50)
        print("✓ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to the server.")
        print("Please make sure the FastAPI server is running:")
        print("  uv run uvicorn main:app --reload")
    except Exception as e:
        print(f"\n✗ Error: {e}")

