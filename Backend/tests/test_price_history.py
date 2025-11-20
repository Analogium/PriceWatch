"""
Test suite for Price History features.

NOTE: These tests use direct database manipulation to test the price history
functionality without depending on external scraping services.

Tests include:
- Price history data structure validation
- Price statistics calculation
- History retrieval and ordering
- Access control and security
"""

import requests
import time
import psycopg2

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "pricewatch",
    "user": "pricewatch",
    "password": "pricewatch",
}

# ANSI color codes
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def print_header(message):
    """Print a formatted header."""
    separator = "=" * 60
    newline = "\n"
    print(f"{newline}{BLUE}{separator}{RESET}")
    print(f"{BLUE}{message}{RESET}")
    print(f"{BLUE}{separator}{RESET}{newline}")


def print_test(test_name, passed, details=""):
    """Print test result."""
    status = f"{GREEN}✓ PASSED{RESET}" if passed else f"{RED}✗ FAILED{RESET}"
    print(f"{status} - {test_name}")
    if details:
        print(f"  {details}")


def register_and_login():
    """Register a new user and login."""
    timestamp = int(time.time())
    test_email = f"testhistory{timestamp}@example.com"
    test_password = "TestPass123!@#"

    # Register
    register_data = {"email": test_email, "password": test_password}
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)

    if response.status_code != 201:
        print(f"{RED}Failed to register user: {response.text}{RESET}")
        return None, None

    # Login
    login_data = {"email": test_email, "password": test_password}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)

    if response.status_code != 200:
        print(f"{RED}Failed to login: {response.text}{RESET}")
        return None, None

    token = response.json()["access_token"]
    return token, test_email


def create_test_product_with_history(token):
    """Create a test product with price history directly in database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Get user ID
        headers = {"Authorization": f"Bearer {token}"}
        user_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)

        if user_response.status_code != 200:
            return None

        user_id = user_response.json()["id"]

        # Insert test product
        cursor.execute(
            """
            INSERT INTO products (user_id, name, url, image, current_price, target_price, last_checked, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """,
            (
                user_id,
                "Test Product for History",
                "https://example.com/test",
                "https://example.com/image.jpg",
                199.99,
                150.0,
            ),
        )

        product_id = cursor.fetchone()[0]

        # Insert multiple price history records
        prices = [199.99, 189.99, 195.50, 175.00, 180.25]
        for i, price in enumerate(prices):
            cursor.execute(
                """
                INSERT INTO price_history (product_id, price, recorded_at)
                VALUES (%s, %s, NOW() - INTERVAL '%s days')
            """,
                (product_id, price, len(prices) - i),
            )

        conn.commit()
        cursor.close()
        conn.close()

        return product_id

    except Exception as e:
        print(f"{RED}Error creating test product: {str(e)}{RESET}")
        return None


def test_price_history_retrieval(token, product_id):
    """Test retrieving price history."""
    print_header("TEST 1: Price History Retrieval")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/products/{product_id}/history", headers=headers)

    if response.status_code == 200:
        history = response.json()
        has_records = len(history) > 0

        if has_records:
            first_record = history[0]
            required_fields = ["id", "product_id", "price", "recorded_at"]
            has_required_fields = all(field in first_record for field in required_fields)

            print_test(
                "Price history retrieval",
                has_required_fields,
                f"Records: {len(history)}, All required fields present: {has_required_fields}",
            )
            return has_required_fields
        else:
            print_test("Price history retrieval", False, "No history records found")
            return False
    else:
        print_test("Price history retrieval", False, f"Status: {response.status_code}")
        return False


def test_price_history_ordering(token, product_id):
    """Test that history is returned in correct order (newest first)."""
    print_header("TEST 2: Price History Ordering")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/products/{product_id}/history", headers=headers)

    if response.status_code == 200:
        history = response.json()

        if len(history) > 1:
            dates = [record["recorded_at"] for record in history]
            is_ordered = all(dates[i] >= dates[i + 1] for i in range(len(dates) - 1))

            print_test(
                "Price history ordering (newest first)",
                is_ordered,
                f"Records: {len(history)}, Properly ordered: {is_ordered}",
            )
            return is_ordered
        else:
            print_test("Price history ordering", True, f"Only {len(history)} record(s), ordering not applicable")
            return True
    else:
        print_test("Price history ordering", False, f"Status: {response.status_code}")
        return False


def test_price_history_limit(token, product_id):
    """Test price history with limit parameter."""
    print_header("TEST 3: Price History Limit Parameter")

    headers = {"Authorization": f"Bearer {token}"}

    # Test with limit=3
    response = requests.get(f"{BASE_URL}/products/{product_id}/history?limit=3", headers=headers)

    if response.status_code == 200:
        history = response.json()
        correct_limit = len(history) <= 3

        print_test("Price history with limit=3", correct_limit, f"Requested: 3, Received: {len(history)}")
        return correct_limit
    else:
        print_test("Price history limit", False, f"Status: {response.status_code}")
        return False


def test_price_statistics(token, product_id):
    """Test price statistics calculation."""
    print_header("TEST 4: Price Statistics")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/products/{product_id}/history/stats", headers=headers)

    if response.status_code == 200:
        stats = response.json()
        required_fields = ["current_price", "lowest_price", "highest_price", "average_price", "total_records"]

        has_all_fields = all(field in stats for field in required_fields)

        if has_all_fields:
            # Check logical consistency
            logical = (
                stats["lowest_price"] <= stats["current_price"]
                and stats["current_price"] <= stats["highest_price"]
                and stats["lowest_price"] <= stats["average_price"] <= stats["highest_price"]
                and stats["total_records"] > 0
            )

            details = (
                f"Current: {stats['current_price']}, Low: {stats['lowest_price']}, "
                f"High: {stats['highest_price']}, Avg: {stats['average_price']}, "
                f"Records: {stats['total_records']}"
            )

            print_test("Price statistics calculation", logical, details)
            return logical
        else:
            print_test("Price statistics calculation", False, f"Missing fields. Expected: {required_fields}")
            return False
    else:
        print_test("Price statistics calculation", False, f"Status: {response.status_code}")
        return False


def test_price_change_percentage(token, product_id):
    """Test price change percentage calculation."""
    print_header("TEST 5: Price Change Percentage")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/products/{product_id}/history/stats", headers=headers)

    if response.status_code == 200:
        stats = response.json()
        has_percentage = "price_change_percentage" in stats

        if has_percentage and stats["price_change_percentage"] is not None:
            percentage = stats["price_change_percentage"]
            is_valid = isinstance(percentage, (int, float))

            print_test("Price change percentage present", is_valid, f"Value: {percentage}%")
            return is_valid
        else:
            print_test("Price change percentage", has_percentage, "Field present but may be null (acceptable)")
            return has_percentage
    else:
        print_test("Price change percentage", False, f"Status: {response.status_code}")
        return False


def test_unauthorized_access(product_id):
    """Test that unauthorized users cannot access price history."""
    print_header("TEST 6: Unauthorized Access Protection")

    # Try without token
    response = requests.get(f"{BASE_URL}/products/{product_id}/history")
    unauthorized = response.status_code in [401, 403]  # 403 is also acceptable (rate limit middleware)

    print_test("Unauthorized access blocked", unauthorized, f"Status: {response.status_code}")

    # Try with invalid token
    headers = {"Authorization": "Bearer invalid_token_12345"}
    response = requests.get(f"{BASE_URL}/products/{product_id}/history", headers=headers)
    invalid_blocked = response.status_code in [401, 422]

    print_test("Invalid token blocked", invalid_blocked, f"Status: {response.status_code}")

    return unauthorized and invalid_blocked


def test_nonexistent_product(token):
    """Test accessing history for non-existent product."""
    print_header("TEST 7: Non-existent Product")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/products/999999/history", headers=headers)

    not_found = response.status_code == 404
    print_test("Non-existent product returns 404", not_found, f"Status: {response.status_code}")

    return not_found


def test_stats_for_nonexistent_product(token):
    """Test statistics for non-existent product."""
    print_header("TEST 8: Statistics for Non-existent Product")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/products/999999/history/stats", headers=headers)

    not_found = response.status_code == 404
    print_test("Statistics for non-existent product returns 404", not_found, f"Status: {response.status_code}")

    return not_found


def main():
    """Run all price history tests."""
    print_header("🧪 PRICE HISTORY FEATURE TESTS")

    results = []

    # Setup
    print_header("SETUP: User Registration and Login")
    token, email = register_and_login()

    if not token:
        print(f"{RED}Setup failed. Cannot proceed with tests.{RESET}")
        return

    print(f"{GREEN}✓ User registered and logged in: {email}{RESET}")

    # Create test product with history
    print_header("SETUP: Creating Test Product with Price History")
    product_id = create_test_product_with_history(token)

    if not product_id:
        print(f"{RED}Failed to create test product. Stopping tests.{RESET}")
        return

    print(f"{GREEN}✓ Test product created with ID: {product_id}{RESET}")

    # Run tests
    try:
        results.append(test_price_history_retrieval(token, product_id))
        results.append(test_price_history_ordering(token, product_id))
        results.append(test_price_history_limit(token, product_id))
        results.append(test_price_statistics(token, product_id))
        results.append(test_price_change_percentage(token, product_id))
        results.append(test_unauthorized_access(product_id))
        results.append(test_nonexistent_product(token))
        results.append(test_stats_for_nonexistent_product(token))

    except Exception as e:
        print(f"{RED}Test execution error: {str(e)}{RESET}")
        import traceback

        traceback.print_exc()

    # Summary
    print_header("TEST SUMMARY")
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0

    print(f"Total tests: {total}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    print(f"{RED}Failed: {total - passed}{RESET}")
    print(f"Success rate: {percentage:.1f}%")

    newline = "\n"
    if percentage == 100:
        print(f"{newline}{GREEN}🎉 All price history tests passed!{RESET}{newline}")
    else:
        print(f"{newline}{YELLOW}⚠️  Some tests failed. Please review the output above.{RESET}{newline}")


if __name__ == "__main__":
    main()
