"""
Test the registration endpoint
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_registration():
    """Test user registration"""
    url = f"{BASE_URL}/api/v1/auth/register"
    
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    print(f"Testing registration at: {url}")
    print(f"Data: {json.dumps(user_data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=user_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("\n✅ Registration successful!")
            return response.json()
        else:
            print("\n❌ Registration failed!")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("   Make sure the backend is running on http://localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_login(email, password):
    """Test user login"""
    url = f"{BASE_URL}/api/v1/auth/login"
    
    login_data = {
        "username": email,
        "password": password
    }
    
    print(f"\nTesting login at: {url}")
    print("-" * 50)
    
    try:
        response = requests.post(
            url,
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ Login successful!")
            return response.json()
        else:
            print("\n❌ Login failed!")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("=" * 50)
    print("Sparta AI - Registration Test")
    print("=" * 50)
    
    # Test registration
    user = test_registration()
    
    if user:
        # Test login
        token_data = test_login("test@example.com", "testpassword123")
        
        if token_data:
            print("\n🎉 All tests passed!")
            print("\nYour access token:")
            print(token_data['access_token'])
