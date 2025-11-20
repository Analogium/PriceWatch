"""
Test script for all security features.
Run this with: python test_security.py
"""

import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_test(test_name):
    separator = "=" * 60
    print(f"\n{BLUE}{separator}{RESET}")
    print(f"{BLUE}TEST: {test_name}{RESET}")
    print(f"{BLUE}{separator}{RESET}")


def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message):
    print(f"{RED}✗ {message}{RESET}")


def print_info(message):
    print(f"{YELLOW}ℹ {message}{RESET}")


def test_1_password_strength():
    """Test password strength validation."""
    print_test("1. Password Strength Validation")

    weak_passwords = [
        ("short", "Short password (< 8 chars)"),
        ("lowercase", "No uppercase letter"),
        ("UPPERCASE", "No lowercase letter"),
        ("NoDigits!", "No digit"),
        ("NoSpecial1", "No special character"),
        ("weakpass", "Multiple violations"),
    ]

    for password, description in weak_passwords:
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json={"email": f"test_{int(time.time())}@example.com", "password": password},
            )
            if response.status_code == 400:
                print_success(f"{description}: Rejected ✓")
            else:
                print_error(f"{description}: Should have been rejected!")
        except Exception as e:
            print_error(f"Error testing {description}: {str(e)}")

    # Test strong password
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={"email": f"strong_user_{int(time.time())}@example.com", "password": "StrongPass123!"},
        )
        if response.status_code == 201:
            print_success("Strong password accepted ✓")
            return response.json()
        else:
            print_error(f"Strong password rejected: {response.json()}")
    except Exception as e:
        print_error(f"Error: {str(e)}")

    return None


def test_2_registration_and_verification():
    """Test user registration with email verification."""
    print_test("2. Registration & Email Verification")

    email = f"verify_test_{int(time.time())}@example.com"
    password = "SecurePass123!"

    try:
        # Register
        response = requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})

        if response.status_code == 201:
            print_success(f"User registered: {email}")
            user_data = response.json()
            print_info(f"User ID: {user_data['id']}")
            print_info(f"Is verified: {user_data.get('is_verified', 'N/A')}")
            print_info("Check your database for verification_token to test email verification")
            return {"email": email, "password": password}
        else:
            print_error(f"Registration failed: {response.json()}")
    except Exception as e:
        print_error(f"Error: {str(e)}")

    return None


def test_3_login_and_tokens():
    """Test login and refresh token functionality."""
    print_test("3. Login & Refresh Tokens")

    # First, create a user
    email = f"token_test_{int(time.time())}@example.com"
    password = "TokenTest123!"

    try:
        # Register
        reg_response = requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})

        if reg_response.status_code != 201:
            print_error(f"Registration failed: {reg_response.json()}")
            return None

        print_success(f"User created: {email}")

        # Login
        login_response = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})

        if login_response.status_code == 200:
            tokens = login_response.json()
            print_success("Login successful")
            print_info(f"Access token received (length: {len(tokens['access_token'])})")
            print_info(f"Refresh token received (length: {len(tokens.get('refresh_token', ''))})")

            # Test access token
            me_response = requests.get(
                f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
            )

            if me_response.status_code == 200:
                print_success(f"Access token valid ✓ User: {me_response.json()['email']}")
            else:
                print_error("Access token invalid")

            # Test refresh token
            if "refresh_token" in tokens:
                refresh_response = requests.post(
                    f"{BASE_URL}/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
                )

                if refresh_response.status_code == 200:
                    new_tokens = refresh_response.json()
                    print_success("Refresh token works ✓")
                    print_info(f"New access token received (length: {len(new_tokens['access_token'])})")
                    return {"tokens": tokens, "email": email}
                else:
                    print_error(f"Refresh token failed: {refresh_response.json()}")
            else:
                print_error("No refresh token received")

        else:
            print_error(f"Login failed: {login_response.json()}")

    except Exception as e:
        print_error(f"Error: {str(e)}")

    return None


def test_4_rate_limiting():
    """Test rate limiting functionality."""
    print_test("4. Rate Limiting")

    print_info("Sending 10 rapid requests to test rate limiting...")

    rate_limited = False
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/../../health")
            print_info(f"Request {i + 1}: Status {response.status_code}")

            if response.status_code == 429:
                print_success(f"Rate limiting triggered after {i + 1} requests ✓")
                rate_limited = True
                break

            time.sleep(0.1)  # Small delay
        except Exception as e:
            print_error(f"Error: {str(e)}")
            break

    if not rate_limited:
        print_info("Rate limit not reached in 10 requests (limit might be higher)")


def test_5_password_reset():
    """Test password reset flow."""
    print_test("5. Password Reset Flow")

    # Create a user first
    email = f"reset_test_{int(time.time())}@example.com"
    password = "OriginalPass123!"

    try:
        # Register
        reg_response = requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})

        if reg_response.status_code != 201:
            print_error(f"Registration failed: {reg_response.json()}")
            return

        print_success(f"User created: {email}")

        # Request password reset
        reset_request = requests.post(f"{BASE_URL}/auth/forgot-password", json={"email": email})

        if reset_request.status_code == 200:
            print_success("Password reset requested ✓")
            print_info("Check your database for reset_token to complete the flow")
            print_info("In production, the token would be sent via email")
        else:
            print_error(f"Password reset request failed: {reset_request.json()}")

        # Test with non-existent email (should return same message for security)
        fake_reset = requests.post(f"{BASE_URL}/auth/forgot-password", json={"email": "nonexistent@example.com"})

        if fake_reset.status_code == 200:
            print_success("Non-existent email handled securely ✓")
        else:
            print_error("Non-existent email response unexpected")

    except Exception as e:
        print_error(f"Error: {str(e)}")


def test_6_duplicate_registration():
    """Test that duplicate emails are rejected."""
    print_test("6. Duplicate Email Prevention")

    email = f"duplicate_test_{int(time.time())}@example.com"
    password = "DuplicateTest123!"

    try:
        # First registration
        response1 = requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})

        if response1.status_code == 201:
            print_success(f"First registration successful: {email}")
        else:
            print_error(f"First registration failed: {response1.json()}")
            return

        # Second registration (should fail)
        response2 = requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})

        if response2.status_code == 400:
            print_success("Duplicate email rejected ✓")
        else:
            print_error(f"Duplicate email was accepted! Status: {response2.status_code}")

    except Exception as e:
        print_error(f"Error: {str(e)}")


def test_7_invalid_credentials():
    """Test login with invalid credentials."""
    print_test("7. Invalid Credentials Handling")

    # Create a user
    email = f"creds_test_{int(time.time())}@example.com"
    password = "CorrectPass123!"

    try:
        # Register
        requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})

        # Test wrong password
        wrong_pass = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": "WrongPass123!"})

        if wrong_pass.status_code == 401:
            print_success("Wrong password rejected ✓")
        else:
            print_error(f"Wrong password accepted! Status: {wrong_pass.status_code}")

        # Test non-existent user
        no_user = requests.post(
            f"{BASE_URL}/auth/login", json={"email": "nonexistent@example.com", "password": password}
        )

        if no_user.status_code == 401:
            print_success("Non-existent user rejected ✓")
        else:
            print_error(f"Non-existent user accepted! Status: {no_user.status_code}")

        # Test correct credentials
        correct = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})

        if correct.status_code == 200:
            print_success("Correct credentials accepted ✓")
        else:
            print_error(f"Correct credentials rejected! Status: {correct.status_code}")

    except Exception as e:
        print_error(f"Error: {str(e)}")


def main():
    separator = "=" * 60
    print(f"\n{GREEN}{separator}")
    print("PriceWatch Security Features Test Suite")
    print(f"{separator}{RESET}\n")

    print_info(f"Testing against: {BASE_URL}")
    print_info("Make sure the backend server is running!")
    print_info("Press Ctrl+C to stop\n")

    try:
        # Run all tests
        test_1_password_strength()
        test_2_registration_and_verification()
        test_3_login_and_tokens()
        test_4_rate_limiting()
        test_5_password_reset()
        test_6_duplicate_registration()
        test_7_invalid_credentials()

        separator = "=" * 60
        print(f"\n{GREEN}{separator}")
        print("All tests completed!")
        print(f"{separator}{RESET}\n")

    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
