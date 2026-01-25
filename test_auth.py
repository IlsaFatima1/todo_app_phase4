import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

def test_auth_flow():
    print("Testing authentication flow...")

    # Step 1: Register a new user
    print("\n1. Registering a new user...")
    register_data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "securepassword123"
    }

    response = requests.post(
        f"{BASE_URL}/auth/register",
        json=register_data
    )

    print(f"Registration response: {response.status_code}")
    print(f"Registration data: {response.text}")

    if response.status_code != 200:
        print("Registration failed!")
        return

    # Step 2: Login with the new user
    print("\n2. Logging in with the new user...")
    login_data = {
        "email": "testuser@example.com",
        "password": "securepassword123"
    }

    # Login requires form data, not JSON
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data=login_data
    )

    print(f"Login response: {response.status_code}")
    print(f"Login data: {response.text}")

    if response.status_code != 200:
        print("Login failed!")
        return

    # Extract token from response
    response_json = response.json()
    token = response_json.get("data", {}).get("access_token")

    if not token:
        print("No token in login response!")
        return

    print(f"\n3. Successfully obtained token: {token[:20]}...")

    # Step 3: Test accessing protected endpoint with token
    print("\n4. Testing protected endpoint with token...")
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        f"{BASE_URL}/todos",
        headers=headers
    )

    print(f"Todos response: {response.status_code}")
    print(f"Todos data: {response.text}")

    print("\nAuthentication flow test completed!")

if __name__ == "__main__":
    test_auth_flow()