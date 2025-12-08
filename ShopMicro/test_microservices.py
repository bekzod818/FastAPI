"""
Complete testing script for ShopMicro microservices
Run this after all services are up and running
"""

import requests
import json
import time
from typing import Optional

BASE_URL = "http://localhost:8000"
GATEWAY_URL = f"{BASE_URL}/api"


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    END = "\033[0m"


class MicroservicesTester:
    def __init__(self):
        self.token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.product_id: Optional[int] = None
        self.order_id: Optional[int] = None
        self.payment_id: Optional[int] = None

    def print_success(self, message: str):
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")

    def print_error(self, message: str):
        print(f"{Colors.RED}✗ {message}{Colors.END}")

    def print_info(self, message: str):
        print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

    def print_section(self, title: str):
        print(f"\n{Colors.YELLOW}{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}{Colors.END}\n")

    def test_health_checks(self):
        """Test health endpoints of all services"""
        self.print_section("1. HEALTH CHECKS")

        services = {
            "API Gateway": f"{BASE_URL}/health",
            "User Service": "http://localhost:8001/health",
            "Product Service": "http://localhost:8002/health",
            "Order Service": "http://localhost:8003/health",
            "Payment Service": "http://localhost:8004/health",
            "Notification Service": "http://localhost:8005/health",
            "Inventory Service": "http://localhost:8006/health",
        }

        for service_name, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.print_success(f"{service_name}: Healthy")
                else:
                    self.print_error(f"{service_name}: Unhealthy")
            except Exception as e:
                self.print_error(f"{service_name}: Unreachable - {str(e)}")

    def test_user_registration(self):
        """Test user registration"""
        self.print_section("2. USER REGISTRATION")

        payload = {
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "TestPass123!",
            "full_name": "Test User",
        }

        try:
            response = requests.post(f"{GATEWAY_URL}/users/register", json=payload)

            if response.status_code == 201:
                data = response.json()
                self.token = data["access_token"]
                self.user_id = data["user"]["id"]
                self.print_success(f"User registered successfully")
                self.print_info(f"User ID: {self.user_id}")
                self.print_info(f"Token: {self.token[:20]}...")
            else:
                self.print_error(f"Registration failed: {response.json()}")
        except Exception as e:
            self.print_error(f"Registration error: {str(e)}")

    def test_user_login(self):
        """Test user login"""
        self.print_section("3. USER LOGIN")

        payload = {"email": "testuser@example.com", "password": "TestPass123!"}

        try:
            response = requests.post(f"{GATEWAY_URL}/users/login", json=payload)

            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self.print_success("Login successful")
            else:
                self.print_error(f"Login failed: {response.json()}")
        except Exception as e:
            self.print_error(f"Login error: {str(e)}")

    def test_create_products(self):
        """Create test products"""
        self.print_section("4. PRODUCT CREATION")

        products = [
            {
                "name": "MacBook Pro",
                "description": "Apple M2 Pro laptop",
                "price": 2499.99,
                "category": "Electronics",
                "sku": "MBP-M2-2023",
            },
            {
                "name": "iPhone 15 Pro",
                "description": "Latest iPhone with titanium design",
                "price": 999.99,
                "category": "Electronics",
                "sku": "IPH-15-PRO",
            },
            {
                "name": "AirPods Pro",
                "description": "Wireless earbuds with ANC",
                "price": 249.99,
                "category": "Audio",
                "sku": "APP-2023",
            },
        ]

        # Create products directly (bypassing gateway for testing)
        for product in products:
            try:
                response = requests.post("http://localhost:8002/products", json=product)

                if response.status_code == 201:
                    data = response.json()
                    if not self.product_id:
                        self.product_id = data["id"]
                    self.print_success(
                        f"Product created: {product['name']} (ID: {data['id']})"
                    )
                else:
                    self.print_error(f"Failed to create {product['name']}")
            except Exception as e:
                self.print_error(f"Error creating product: {str(e)}")

    def test_add_inventory(self):
        """Add inventory for products"""
        self.print_section("5. INVENTORY MANAGEMENT")

        if not self.product_id:
            self.print_error("No products available")
            return

        # Add inventory for first 3 products
        for product_id in range(1, 4):
            payload = {
                "product_id": product_id,
                "available_quantity": 50,
                "reorder_level": 10,
            }

            try:
                response = requests.post(
                    "http://localhost:8006/inventory", json=payload
                )

                if response.status_code == 201:
                    self.print_success(
                        f"Inventory added for Product {product_id}: 50 units"
                    )
                else:
                    self.print_info(
                        f"Product {product_id}: {response.json().get('detail', 'Already exists')}"
                    )
            except Exception as e:
                self.print_error(f"Inventory error: {str(e)}")

    def test_list_products(self):
        """List all products"""
        self.print_section("6. PRODUCT LISTING")

        try:
            response = requests.get(f"{GATEWAY_URL}/products")

            if response.status_code == 200:
                products = response.json()
                self.print_success(f"Found {len(products)} products")
                for product in products:
                    self.print_info(f"  - {product['name']}: ${product['price']}")
            else:
                self.print_error("Failed to list products")
        except Exception as e:
            self.print_error(f"Error listing products: {str(e)}")

    def test_create_order(self):
        """Create an order"""
        self.print_section("7. ORDER CREATION")

        if not self.token:
            self.print_error("No authentication token")
            return

        payload = {
            "items": [
                {"product_id": 1, "quantity": 1},
                {"product_id": 3, "quantity": 2},
            ]
        }

        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.post(
                f"{GATEWAY_URL}/orders", json=payload, headers=headers
            )

            if response.status_code == 201:
                data = response.json()
                self.order_id = data["id"]
                self.print_success(f"Order created successfully")
                self.print_info(f"Order ID: {self.order_id}")
                self.print_info(f"Total Amount: ${data['total_amount']}")
                self.print_info(f"Status: {data['status']}")
            else:
                self.print_error(f"Order creation failed: {response.json()}")
        except Exception as e:
            self.print_error(f"Order error: {str(e)}")

    def test_process_payment(self):
        """Process payment for order"""
        self.print_section("8. PAYMENT PROCESSING")

        if not self.token or not self.order_id:
            self.print_error("No order to pay for")
            return

        payload = {
            "order_id": self.order_id,
            "amount": 2999.97,  # Approximate total
            "payment_method": "credit_card",
            "card_number": "4242",
            "card_holder": "Test User",
        }

        headers = {"Authorization": f"Bearer {self.token}"}

        try:
            response = requests.post(
                f"{GATEWAY_URL}/payments", json=payload, headers=headers
            )

            if response.status_code == 201:
                data = response.json()
                self.payment_id = data["id"]
                self.print_success("Payment processed successfully")
                self.print_info(f"Payment ID: {self.payment_id}")
                self.print_info(f"Transaction ID: {data['transaction_id']}")
                self.print_info(f"Status: {data['status']}")
            else:
                self.print_error(f"Payment failed: {response.json()}")
        except Exception as e:
            self.print_error(f"Payment error: {str(e)}")

    def test_get_notifications(self):
        """Check notifications"""
        self.print_section("9. NOTIFICATIONS")

        if not self.user_id:
            self.print_error("No user ID")
            return

        try:
            response = requests.get(
                f"http://localhost:8005/notifications/user/{self.user_id}"
            )

            if response.status_code == 200:
                notifications = response.json()
                self.print_success(f"Found {len(notifications)} notifications")
                for notif in notifications[:3]:  # Show first 3
                    self.print_info(f"  - {notif['type']}: {notif['message']}")
            else:
                self.print_info("No notifications yet")
        except Exception as e:
            self.print_error(f"Notification error: {str(e)}")

    def test_inventory_check(self):
        """Check inventory levels"""
        self.print_section("10. INVENTORY CHECK")

        for product_id in range(1, 4):
            try:
                response = requests.get(f"http://localhost:8006/inventory/{product_id}")

                if response.status_code == 200:
                    data = response.json()
                    self.print_success(f"Product {product_id} Inventory:")
                    self.print_info(f"  Available: {data['available_quantity']}")
                    self.print_info(f"  Reserved: {data['reserved_quantity']}")
                    self.print_info(f"  Needs Reorder: {data['needs_reorder']}")
            except Exception as e:
                self.print_error(f"Error checking inventory: {str(e)}")

    def run_all_tests(self):
        """Run complete test suite"""
        self.print_section("SHOPMICRO MICROSERVICES TEST SUITE")

        tests = [
            self.test_health_checks,
            self.test_user_registration,
            self.test_user_login,
            self.test_create_products,
            self.test_add_inventory,
            self.test_list_products,
            self.test_create_order,
            self.test_process_payment,
            self.test_get_notifications,
            self.test_inventory_check,
        ]

        for test in tests:
            try:
                test()
                time.sleep(1)  # Small delay between tests
            except Exception as e:
                self.print_error(f"Test failed: {str(e)}")

        self.print_section("TEST SUITE COMPLETED")
        self.print_success("All tests executed!")


if __name__ == "__main__":
    print(f"\n{Colors.BLUE}{'=' * 60}")
    print("  ShopMicro Microservices Test Suite")
    print("  Testing all services and their interactions")
    print(f"{'=' * 60}{Colors.END}\n")

    tester = MicroservicesTester()
    tester.run_all_tests()

    print(f"\n{Colors.GREEN}Testing completed! Check the results above.{Colors.END}\n")
