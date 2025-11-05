"""
Script de test simple pour vérifier que l'API fonctionne correctement.
Usage: python test_api.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint."""
    print("\n🔍 Test 1: Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_register():
    """Test user registration."""
    print("\n🔍 Test 2: User Registration")
    data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code in [200, 201, 400]  # 400 si l'utilisateur existe déjà

def test_login():
    """Test user login and get token."""
    print("\n🔍 Test 3: User Login")
    data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")

    if response.status_code == 200:
        return result.get("access_token")
    return None

def test_get_me(token):
    """Test getting current user info."""
    print("\n🔍 Test 4: Get Current User")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_add_product(token):
    """Test adding a product to track."""
    print("\n🔍 Test 5: Add Product (Amazon example)")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "url": "https://www.amazon.fr/dp/B0EXAMPLE",
        "target_price": 199.99
    }
    response = requests.post(f"{BASE_URL}/api/v1/products", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        print(f"Response: {response.json()}")
        return response.json().get("id")
    else:
        print(f"Response: {response.text}")
        return None

def test_get_products(token):
    """Test getting all products."""
    print("\n🔍 Test 6: Get All Products")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/products", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def main():
    """Run all tests."""
    print("=" * 50)
    print("🧪 PriceWatch API Tests")
    print("=" * 50)

    # Test 1: Health check
    if not test_health():
        print("\n❌ Health check failed! Is the server running?")
        return

    # Test 2: Register
    test_register()

    # Test 3: Login
    token = test_login()
    if not token:
        print("\n❌ Login failed! Cannot continue tests.")
        return

    # Test 4: Get current user
    test_get_me(token)

    # Test 5: Add product (might fail due to scraping, that's ok)
    product_id = test_add_product(token)

    # Test 6: Get all products
    test_get_products(token)

    print("\n" + "=" * 50)
    print("✅ Tests terminés!")
    print("=" * 50)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Erreur: Impossible de se connecter au serveur.")
        print("Assurez-vous que le backend est lancé sur http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {str(e)}")
