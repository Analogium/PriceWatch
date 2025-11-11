"""
Test suite for Pagination, Filtering, and Sorting features.

Tests include:
- Pagination (page, page_size, metadata)
- Sorting (by name, price, date, etc.)
- Filtering/Search (by name and URL)
- Combined features
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
    "password": "pricewatch"
}

# ANSI color codes
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'


def print_header(message):
    """Print a formatted header."""
    separator = '=' * 60
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
    test_email = f"testpagination{timestamp}@example.com"
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


def create_test_products(token, count=25):
    """Create multiple test products directly in database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Get user ID
        headers = {"Authorization": f"Bearer {token}"}
        user_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)

        if user_response.status_code != 200:
            return []

        user_id = user_response.json()["id"]

        product_ids = []

        # Insert multiple test products with varying prices
        for i in range(count):
            price = 100 + (i * 10)
            cursor.execute("""
                INSERT INTO products (user_id, name, url, image, current_price, target_price, last_checked, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW() - INTERVAL '%s days', NOW() - INTERVAL '%s days')
                RETURNING id
            """, (
                user_id,
                f"Product {i+1:02d}",
                f"https://example.com/product{i+1}",
                f"https://example.com/image{i+1}.jpg",
                price,
                price - 20,
                count - i,  # Older products have higher numbers
                count - i
            ))

            product_id = cursor.fetchone()[0]
            product_ids.append(product_id)

        conn.commit()
        cursor.close()
        conn.close()

        return product_ids

    except Exception as e:
        print(f"{RED}Error creating test products: {str(e)}{RESET}")
        return []


def test_basic_pagination(token):
    """Test basic pagination functionality."""
    print_header("TEST 1: Basic Pagination")

    headers = {"Authorization": f"Bearer {token}"}

    # Test page 1
    response = requests.get(f"{BASE_URL}/products?page=1&page_size=10", headers=headers)

    if response.status_code == 200:
        data = response.json()
        has_items = "items" in data and "metadata" in data
        correct_page_size = len(data["items"]) <= 10

        metadata = data.get("metadata", {})
        correct_metadata = (
            metadata.get("page") == 1 and
            metadata.get("page_size") == 10 and
            "total_items" in metadata and
            "total_pages" in metadata and
            "has_next" in metadata and
            "has_previous" in metadata
        )

        print_test(
            "Basic pagination structure",
            has_items and correct_page_size and correct_metadata,
            f"Items: {len(data.get('items', []))}, Metadata valid: {correct_metadata}"
        )
        return has_items and correct_page_size and correct_metadata
    else:
        print_test("Basic pagination", False, f"Status: {response.status_code}")
        return False


def test_pagination_metadata(token):
    """Test pagination metadata accuracy."""
    print_header("TEST 2: Pagination Metadata")

    headers = {"Authorization": f"Bearer {token}"}

    # Get first page with page_size=5
    response = requests.get(f"{BASE_URL}/products?page=1&page_size=5", headers=headers)

    if response.status_code == 200:
        data = response.json()
        metadata = data["metadata"]

        # Check has_previous and has_next
        first_page_correct = metadata["has_previous"] == False and metadata["has_next"] == True

        # Get middle page
        response2 = requests.get(f"{BASE_URL}/products?page=2&page_size=5", headers=headers)
        if response2.status_code == 200:
            data2 = response2.json()
            metadata2 = data2["metadata"]
            middle_page_correct = metadata2["has_previous"] == True

            print_test(
                "Pagination metadata accuracy",
                first_page_correct and middle_page_correct,
                f"First page has_next: {metadata['has_next']}, Middle page has_previous: {metadata2['has_previous']}"
            )
            return first_page_correct and middle_page_correct
        else:
            print_test("Pagination metadata", False, "Failed to get second page")
            return False
    else:
        print_test("Pagination metadata", False, f"Status: {response.status_code}")
        return False


def test_sorting_by_price(token):
    """Test sorting by price."""
    print_header("TEST 3: Sorting by Price")

    headers = {"Authorization": f"Bearer {token}"}

    # Sort by price ascending
    response = requests.get(
        f"{BASE_URL}/products?page=1&page_size=5&sort_by=current_price&order=asc",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        items = data["items"]

        if len(items) >= 2:
            prices = [item["current_price"] for item in items]
            is_ascending = all(prices[i] <= prices[i+1] for i in range(len(prices)-1))

            print_test(
                "Sorting by price (ascending)",
                is_ascending,
                f"Prices: {prices[:3]}..."
            )
            return is_ascending
        else:
            print_test("Sorting by price", True, "Not enough items to test sorting")
            return True
    else:
        print_test("Sorting by price", False, f"Status: {response.status_code}")
        return False


def test_sorting_by_name(token):
    """Test sorting by name."""
    print_header("TEST 4: Sorting by Name")

    headers = {"Authorization": f"Bearer {token}"}

    # Sort by name ascending
    response = requests.get(
        f"{BASE_URL}/products?page=1&page_size=5&sort_by=name&order=asc",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        items = data["items"]

        if len(items) >= 2:
            names = [item["name"] for item in items]
            is_ascending = all(names[i] <= names[i+1] for i in range(len(names)-1))

            print_test(
                "Sorting by name (ascending)",
                is_ascending,
                f"Names: {names[:3]}"
            )
            return is_ascending
        else:
            print_test("Sorting by name", True, "Not enough items to test sorting")
            return True
    else:
        print_test("Sorting by name", False, f"Status: {response.status_code}")
        return False


def test_search_by_name(token):
    """Test search functionality by name."""
    print_header("TEST 5: Search by Name")

    headers = {"Authorization": f"Bearer {token}"}

    # Search for "Product 01"
    response = requests.get(
        f"{BASE_URL}/products?search=Product 01",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        items = data["items"]

        # Check that all results contain the search term
        all_match = all("Product 01" in item["name"] or "Product 01" in item["url"] for item in items)

        print_test(
            "Search by name",
            all_match,
            f"Found {len(items)} items matching 'Product 01'"
        )
        return all_match
    else:
        print_test("Search by name", False, f"Status: {response.status_code}")
        return False


def test_search_by_url(token):
    """Test search functionality by URL."""
    print_header("TEST 6: Search by URL")

    headers = {"Authorization": f"Bearer {token}"}

    # Search by URL pattern
    response = requests.get(
        f"{BASE_URL}/products?search=product1",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        items = data["items"]

        # Check that results contain the search term in name or URL
        search_term_lower = "product1"
        all_match = all(
            search_term_lower in item["name"].lower() or search_term_lower in item["url"].lower()
            for item in items
        )

        print_test(
            "Search by URL pattern",
            all_match,
            f"Found {len(items)} items matching 'product1'"
        )
        return all_match
    else:
        print_test("Search by URL", False, f"Status: {response.status_code}")
        return False


def test_combined_search_and_sort(token):
    """Test combining search and sort."""
    print_header("TEST 7: Combined Search and Sort")

    headers = {"Authorization": f"Bearer {token}"}

    # Search and sort by price
    response = requests.get(
        f"{BASE_URL}/products?search=Product&sort_by=current_price&order=desc",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        items = data["items"]

        if len(items) >= 2:
            # Check search filter applied
            all_match_search = all("Product" in item["name"] or "Product" in item["url"] for item in items)

            # Check sorting applied
            prices = [item["current_price"] for item in items]
            is_descending = all(prices[i] >= prices[i+1] for i in range(len(prices)-1))

            print_test(
                "Combined search and sort",
                all_match_search and is_descending,
                f"Found {len(items)} items, sorted descending: {is_descending}"
            )
            return all_match_search and is_descending
        else:
            print_test("Combined search and sort", True, "Not enough items to test")
            return True
    else:
        print_test("Combined search and sort", False, f"Status: {response.status_code}")
        return False


def test_empty_search_results(token):
    """Test search with no results."""
    print_header("TEST 8: Empty Search Results")

    headers = {"Authorization": f"Bearer {token}"}

    # Search for something that doesn't exist
    response = requests.get(
        f"{BASE_URL}/products?search=NonExistentProduct12345",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        items = data["items"]
        metadata = data["metadata"]

        empty_results = len(items) == 0 and metadata["total_items"] == 0

        print_test(
            "Empty search results handled correctly",
            empty_results,
            f"Items: {len(items)}, Total: {metadata['total_items']}"
        )
        return empty_results
    else:
        print_test("Empty search results", False, f"Status: {response.status_code}")
        return False


def main():
    """Run all pagination tests."""
    print_header("🧪 PAGINATION, FILTERING & SORTING TESTS")

    results = []

    # Setup
    print_header("SETUP: User Registration and Login")
    token, email = register_and_login()

    if not token:
        print(f"{RED}Setup failed. Cannot proceed with tests.{RESET}")
        return

    print(f"{GREEN}✓ User registered and logged in: {email}{RESET}")

    # Create test products
    print_header("SETUP: Creating Test Products")
    product_ids = create_test_products(token, count=25)

    if len(product_ids) == 0:
        print(f"{RED}Failed to create test products. Stopping tests.{RESET}")
        return

    print(f"{GREEN}✓ Created {len(product_ids)} test products{RESET}")

    # Wait a moment for database operations to complete
    time.sleep(1)

    # Run tests
    try:
        results.append(test_basic_pagination(token))
        results.append(test_pagination_metadata(token))
        results.append(test_sorting_by_price(token))
        results.append(test_sorting_by_name(token))
        results.append(test_search_by_name(token))
        results.append(test_search_by_url(token))
        results.append(test_combined_search_and_sort(token))
        results.append(test_empty_search_results(token))

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
        print(f"{newline}{GREEN}🎉 All pagination tests passed!{RESET}{newline}")
    else:
        print(f"{newline}{YELLOW}⚠️  Some tests failed. Please review the output above.{RESET}{newline}")


if __name__ == "__main__":
    main()
