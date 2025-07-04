import requests
import json
import time
import jwt
from datetime import datetime, timedelta

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://8322c09e-45ff-49e6-ae77-baef7fc3717c.preview.emergentagent.com/api"

# Test credentials
ADMIN_EMAIL = "admin@shophub.com"
ADMIN_PASSWORD = "admin123"
CUSTOMER_EMAIL = "customer1@example.com"
CUSTOMER_PASSWORD = "customer123"

# Helper functions
def print_test_result(test_name: str, success: bool, details: str = ""):
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"{status} - {test_name}")
    if details:
        print(f"  Details: {details}")
    print()

def get_headers(token: str):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

class JWTAuthTests:
    @staticmethod
    def test_login_jwt_token_generation():
        """Test JWT token generation during login"""
        response = requests.post(
            f"{BACKEND_URL}/login",
            json={"email": CUSTOMER_EMAIL, "password": CUSTOMER_PASSWORD}
        )
        
        success = response.status_code == 200
        details = ""
        
        if success:
            data = response.json()
            token = data.get("token")
            
            # Check if token exists
            if not token:
                success = False
                details = "No token returned in login response"
            else:
                # Try to decode the token (without verification)
                try:
                    decoded = jwt.decode(token, options={"verify_signature": False})
                    if "user_id" in decoded and "exp" in decoded:
                        details = f"JWT token successfully generated with user_id and expiration"
                    else:
                        success = False
                        details = f"JWT token missing required claims: {decoded}"
                except Exception as e:
                    success = False
                    details = f"Failed to decode JWT token: {str(e)}"
        else:
            details = f"Login failed: {response.status_code} - {response.text}"
        
        print_test_result("JWT Token Generation", success, details)
        return success, token if success else None

    @staticmethod
    def test_protected_route_with_valid_token(token):
        """Test accessing a protected route with a valid token"""
        if not token:
            print_test_result("Protected Route Access (Valid Token)", False, "No token available")
            return False
            
        response = requests.get(
            f"{BACKEND_URL}/me",
            headers=get_headers(token)
        )
        
        success = response.status_code == 200
        details = ""
        
        if success:
            data = response.json()
            details = f"Successfully accessed protected route with valid token. User: {data.get('email')}"
        else:
            details = f"Failed to access protected route: {response.status_code} - {response.text}"
        
        print_test_result("Protected Route Access (Valid Token)", success, details)
        return success

    @staticmethod
    def test_protected_route_with_invalid_token():
        """Test accessing a protected route with an invalid token"""
        invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTIzNDU2Nzg5MCIsImV4cCI6MTY5MDAwMDAwMH0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        
        response = requests.get(
            f"{BACKEND_URL}/me",
            headers=get_headers(invalid_token)
        )
        
        # Should fail with 401 Unauthorized
        success = response.status_code == 401
        details = ""
        
        if success:
            details = "Correctly rejected invalid token"
        else:
            details = f"Failed to reject invalid token: {response.status_code} - {response.text}"
        
        print_test_result("Protected Route Access (Invalid Token)", success, details)
        return success

    @staticmethod
    def test_protected_route_without_token():
        """Test accessing a protected route without a token"""
        response = requests.get(f"{BACKEND_URL}/me")
        
        # Should fail with 401 or 403
        success = response.status_code in [401, 403]
        details = ""
        
        if success:
            details = f"Correctly rejected request without token (status: {response.status_code})"
        else:
            details = f"Failed to reject request without token: {response.status_code} - {response.text}"
        
        print_test_result("Protected Route Access (No Token)", success, details)
        return success

    @staticmethod
    def test_admin_route_with_customer_token(token):
        """Test accessing an admin route with a customer token"""
        if not token:
            print_test_result("Admin Route Access (Customer Token)", False, "No token available")
            return False
            
        response = requests.get(
            f"{BACKEND_URL}/admin/stats",
            headers=get_headers(token)
        )
        
        # Should fail with 403 Forbidden
        success = response.status_code == 403
        details = ""
        
        if success:
            details = "Correctly denied customer access to admin route"
        else:
            details = f"Failed to deny customer access to admin route: {response.status_code} - {response.text}"
        
        print_test_result("Admin Route Access (Customer Token)", success, details)
        return success

    @staticmethod
    def test_admin_route_with_admin_token():
        """Test accessing an admin route with an admin token"""
        # Login as admin
        response = requests.post(
            f"{BACKEND_URL}/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        if response.status_code != 200:
            print_test_result("Admin Route Access (Admin Token)", False, "Admin login failed")
            return False
            
        admin_token = response.json().get("token")
        
        response = requests.get(
            f"{BACKEND_URL}/admin/stats",
            headers=get_headers(admin_token)
        )
        
        success = response.status_code == 200
        details = ""
        
        if success:
            data = response.json()
            details = f"Successfully accessed admin route with admin token. Stats: {data}"
        else:
            details = f"Failed to access admin route with admin token: {response.status_code} - {response.text}"
        
        print_test_result("Admin Route Access (Admin Token)", success, details)
        return success

def run_jwt_auth_tests():
    print("=" * 80)
    print("STARTING JWT AUTHENTICATION TESTS")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print("-" * 80)
    
    jwt_tests = JWTAuthTests()
    
    # Test JWT token generation
    success, token = jwt_tests.test_login_jwt_token_generation()
    
    # Test protected routes with valid token
    if success:
        jwt_tests.test_protected_route_with_valid_token(token)
        jwt_tests.test_admin_route_with_customer_token(token)
    
    # Test invalid token scenarios
    jwt_tests.test_protected_route_with_invalid_token()
    jwt_tests.test_protected_route_without_token()
    
    # Test admin route with admin token
    jwt_tests.test_admin_route_with_admin_token()
    
    print("=" * 80)
    print("JWT AUTHENTICATION TESTS COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    run_jwt_auth_tests()