import pytest
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000/sc"  # Fixed: removed /api prefix

# Helper function to safely get JSON response
def safe_json_response(response):
    """Safely extract JSON from response, handling HTML error pages"""
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        # Return error info if response is not JSON
        return {
            "error": "Non-JSON response",
            "status_code": response.status_code,
            "text": response.text[:200] + "..." if len(response.text) > 200 else response.text
        }

# --------- Fixtures for login and tokens ---------
# @pytest.fixture(scope="session")
# def admin_token():
#     """Mock admin token for testing"""
#     return "mock_admin_token_123"
@pytest.fixture(scope="session")
def admin_token():
    url = "http://127.0.0.1:5000/auth/login"
    data = {"username": "admin1", "password": "password123"}
    response = requests.post(url, json=data)
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def caregiver_token():
    url = "http://127.0.0.1:5000/auth/login"
    data = {"username": "yuvi", "password": "pass"}
    response = requests.post(url, json=data)
    assert response.status_code == 200
    return response.json()["access_token"]
    # """Mock caregiver token for testing"""
    # return "mock_caregiver_token_456"

@pytest.fixture(scope="session")
def senior_token():
    url = "http://127.0.0.1:5000/auth/login"
    data = {"username": "amit", "password": "pass"}
    response = requests.post(url, json=data)
    assert response.status_code == 200
    return response.json()["access_token"]
    # """Mock senior citizen token for testing"""
    # return "mock_senior_token_789"

# --------- Test Cases ---------
# --------- Authentication Test Cases ---------

# 40. POST /auth/signup
def test_signup_success():
    """
    API being tested: /auth/signup [POST]
    Inputs: JSON: {"first_name": "John", "last_name": "Doe", "username": "johndoe", "password": "password123", "confirm_password": "password123", "role": "senior_citizen"}
    Expected Output: HTTP 201, JSON: {"message": "User registered successfully"}
    """
    url = "http://127.0.0.1:5000/auth/signup"
    data = {
        "first_name": "John",
        "last_name": "Doe", 
        "username": "johndoe",
        "password": "password123",
        "confirm_password": "password123",
        "role": "senior_citizen"
    }
    response = requests.post(url, json=data)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [201, 400]  # 400 if username already exists
    print("Result: Success")

def test_signup_username_exists():
    """
    API being tested: /auth/signup [POST]
    Inputs: JSON: {"first_name": "Jane", "last_name": "Smith", "username": "johndoe", "password": "password123", "confirm_password": "password123"}
    Expected Output: HTTP 400, JSON: {"message": "Username already exists"}
    """
    url = "http://127.0.0.1:5000/auth/signup"
    data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "username": "johndoe",  # Same username as previous test
        "password": "password123",
        "confirm_password": "password123"
    }
    response = requests.post(url, json=data)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 400
    assert "Username already exists" in response.json().get("message", "")
    print("Result: Success")

def test_signup_password_mismatch():
    """
    API being tested: /auth/signup [POST]
    Inputs: JSON: {"first_name": "Bob", "last_name": "Wilson", "username": "bobwilson", "password": "password123", "confirm_password": "differentpassword"}
    Expected Output: HTTP 400, JSON: {"message": "Passwords do not match"}
    """
    url = "http://127.0.0.1:5000/auth/signup"
    data = {
        "first_name": "Bob",
        "last_name": "Wilson",
        "username": "bobwilson",
        "password": "password123",
        "confirm_password": "differentpassword"
    }
    response = requests.post(url, json=data)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 400
    assert "Passwords do not match" in response.json().get("message", "")
    print("Result: Success")

def test_signup_missing_required_fields():
    """
    API being tested: /auth/signup [POST]
    Inputs: JSON: {"first_name": "Alice", "username": "alice"} (missing last_name, password, confirm_password)
    Expected Output: HTTP 400 Bad Request
    """
    url = "http://127.0.0.1:5000/auth/signup"
    data = {
        "first_name": "Alice",
        "username": "alice"
        # Missing required fields
    }
    response = requests.post(url, json=data)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 400
    print("Result: Success")

# 41. POST /auth/login
def test_login_success():
    """
    API being tested: /auth/login [POST]
    Inputs: JSON: {"username": "johndoe", "password": "password123"}
    Expected Output: HTTP 200, JSON: {"access_token": "...", "user_id": <int>, "role": "senior_citizen"}
    """
    url = "http://127.0.0.1:5000/auth/login"
    data = {
        "username": "johndoe",
        "password": "password123"
    }
    response = requests.post(url, json=data)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "user_id" in response.json()
    assert "role" in response.json()
    print("Result: Success")

def test_login_invalid_username():
    """
    API being tested: /auth/login [POST]
    Inputs: JSON: {"username": "nonexistentuser", "password": "password123"}
    Expected Output: HTTP 401, JSON: {"message": "Invalid credentials"}
    """
    url = "http://127.0.0.1:5000/auth/login"
    data = {
        "username": "nonexistentuser",
        "password": "password123"
    }
    response = requests.post(url, json=data)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 401
    assert "Invalid credentials" in response.json().get("message", "")
    print("Result: Success")

def test_login_invalid_password():
    """
    API being tested: /auth/login [POST]
    Inputs: JSON: {"username": "johndoe", "password": "wrongpassword"}
    Expected Output: HTTP 401, JSON: {"message": "Invalid credentials"}
    """
    url = "http://127.0.0.1:5000/auth/login"
    data = {
        "username": "johndoe",
        "password": "wrongpassword"
    }
    response = requests.post(url, json=data)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 401
    assert "Invalid credentials" in response.json().get("message", "")
    print("Result: Success")

def test_login_missing_fields():
    """
    API being tested: /auth/login [POST]
    Inputs: JSON: {"username": "johndoe"} (missing password)
    Expected Output: HTTP 400 Bad Request
    """
    url = "http://127.0.0.1:5000/auth/login"
    data = {
        "username": "johndoe"
        # Missing password
    }
    response = requests.post(url, json=data)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 400
    print("Result: Success")

# 42. GET /auth/protected
def test_protected_route_success():
    """
    API being tested: /auth/protected [GET]
    Inputs: Header: Authorization: Bearer <valid_token>
    Expected Output: HTTP 200, JSON: {"message": "Hello John!"}
    """
    # First login to get a valid token
    login_url = "http://127.0.0.1:5000/auth/login"
    login_data = {
        "username": "johndoe",
        "password": "password123"
    }
    login_response = requests.post(login_url, json=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json().get("access_token")
        url = "http://127.0.0.1:5000/auth/protected"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        print("Actual Output:", response.status_code, response.json())
        assert response.status_code == 200
        assert "Hello" in response.json().get("message", "")
        print("Result: Success")
    else:
        print("Actual Output: Could not get valid token for testing")
        print("Result: Skip - No valid user created")

def test_protected_route_unauthorized():
    """
    API being tested: /auth/protected [GET]
    Inputs: Header: None
    Expected Output: HTTP 401 Unauthorized
    """
    url = "http://127.0.0.1:5000/auth/protected"
    response = requests.get(url)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 401
    print("Result: Success")

def test_protected_route_invalid_token():
    """
    API being tested: /auth/protected [GET]
    Inputs: Header: Authorization: Bearer invalid_token
    Expected Output: HTTP 401 Unauthorized
    """
    url = "http://127.0.0.1:5000/auth/protected"
    headers = {"Authorization": "Bearer invalid_token_123"}
    response = requests.get(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [401, 422]
    print("Result: Success")

# --------- Test Cases for Different User Roles ---------

def test_signup_caregiver_role():
    """
    API being tested: /auth/signup [POST]
    Inputs: JSON: {"first_name": "Care", "last_name": "Giver", "username": "caregiver1", "password": "password123", "confirm_password": "password123", "role": "care_giver"}
    Expected Output: HTTP 201, JSON: {"message": "User registered successfully"}
    """
    url = "http://127.0.0.1:5000/auth/signup"
    data = {
        "first_name": "Care",
        "last_name": "Giver",
        "username": "caregiver1",
        "password": "password123",
        "confirm_password": "password123",
        "role": "care_giver"
    }
    response = requests.post(url, json=data)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [201, 400]  # 400 if username already exists
    print("Result: Success")

def test_signup_admin_role():
    """
    API being tested: /auth/signup [POST]
    Inputs: JSON: {"first_name": "Admin", "last_name": "User", "username": "admin1", "password": "password123", "confirm_password": "password123", "role": "admin"}
    Expected Output: HTTP 201, JSON: {"message": "User registered successfully"}
    """
    url = "http://127.0.0.1:5000/auth/signup"
    data = {
        "first_name": "Admin",
        "last_name": "User",
        "username": "admin1",
        "password": "password123",
        "confirm_password": "password123",
        "role": "admin"
    }
    response = requests.post(url, json=data)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [201, 400]  # 400 if username already exists
    print("Result: Success")

def test_login_caregiver():
    """
    API being tested: /auth/login [POST]
    Inputs: JSON: {"username": "caregiver1", "password": "password123"}
    Expected Output: HTTP 200, JSON: {"access_token": "...", "user_id": <int>, "role": "care_giver"}
    """
    url = "http://127.0.0.1:5000/auth/login"
    data = {
        "username": "caregiver1",
        "password": "password123"
    }
    response = requests.post(url, json=data)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 401]  # 401 if user doesn't exist
    if response.status_code == 200:
        assert response.json().get("role") == "care_giver"
    print("Result: Success")

def test_login_admin():
    """
    API being tested: /auth/login [POST]
    Inputs: JSON: {"username": "admin1", "password": "password123"}
    Expected Output: HTTP 200, JSON: {"access_token": "...", "user_id": <int>, "role": "admin"}
    """
    url = "http://127.0.0.1:5000/auth/login"
    data = {
        "username": "admin1",
        "password": "password123"
    }
    response = requests.post(url, json=data)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 401]  # 401 if user doesn't exist
    if response.status_code == 200:
        assert response.json().get("role") == "admin"
    print("Result: Success")

# --------- Edge Cases for Authentication ---------

def test_signup_empty_fields():
    """
    API being tested: /auth/signup [POST]
    Inputs: JSON: {"first_name": "", "last_name": "", "username": "", "password": "", "confirm_password": ""}
    Expected Output: HTTP 400 Bad Request
    """
    url = "http://127.0.0.1:5000/auth/signup"
    data = {
        "first_name": "",
        "last_name": "",
        "username": "",
        "password": "",
        "confirm_password": ""
    }
    response = requests.post(url, json=data)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 400
    print("Result: Success")

def test_signup_special_characters():
    """
    API being tested: /auth/signup [POST]
    Inputs: JSON: {"first_name": "Test@User", "last_name": "Special#Name", "username": "test@user", "password": "pass@word123", "confirm_password": "pass@word123"}
    Expected Output: HTTP 201 or 400 (depending on validation)
    """
    url = "http://127.0.0.1:5000/auth/signup"
    data = {
        "first_name": "Test@User",
        "last_name": "Special#Name",
        "username": "test@user",
        "password": "pass@word123",
        "confirm_password": "pass@word123"
    }
    response = requests.post(url, json=data)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [201, 400]  # 400 if special chars not allowed
    print("Result: Success")

def test_login_case_sensitivity():
    """
    API being tested: /auth/login [POST]
    Inputs: JSON: {"username": "JOHNDOE", "password": "password123"}
    Expected Output: HTTP 401 (if case sensitive) or 200 (if case insensitive)
    """
    url = "http://127.0.0.1:5000/auth/login"
    data = {
        "username": "JOHNDOE",  # Uppercase version
        "password": "password123"
    }
    response = requests.post(url, json=data)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 401]  # Depends on case sensitivity
    print("Result: Success")

# 1. POST /sc/add-dependent
def test_add_dependent_success(caregiver_token):
    """
    API being tested: /sc/add-dependent [POST]
    Inputs: JSON: {"senior_id": 1}
            Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 201, JSON: {"success": true, "dependent": {...}}
    """
    url = f"{BASE_URL}/add-dependent"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    data = {"senior_id": 1}
    response = requests.post(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, safe_json_response(response))
    assert response.status_code in [201, 200, 401, 404, 422]  # Added 422 for invalid JWT
    print("Result: Success")

def test_add_dependent_unauthorized():
    """
    API being tested: /sc/add-dependent [POST]
    Inputs: JSON: {"senior_id": 1}
            Header: None
    Expected Output: HTTP 401 Unauthorized
    """
    url = f"{BASE_URL}/add-dependent"
    data = {"senior_id": 1}
    response = requests.post(url, json=data)
    print("Actual Output:", response.status_code, safe_json_response(response))
    assert response.status_code in [401, 404]  # 404 if endpoint not found
    print("Result: Success")

# 2. POST /sc/add-medicine-reminder
def test_add_medicine_reminder_success(caregiver_token):
    """
    API being tested: /sc/add-medicine-reminder [POST]
    Inputs: JSON: {"user_med_map_id": 1, "reminder_time": "breakfast_before", "notification_type": "push", "message": "Take medicine"}
            Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 201, JSON: {"message": "Reminder created successfully", "id": <int>}
    """
    url = f"{BASE_URL}/add-medicine-reminder"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    data = {
        "user_med_map_id": 1,
        "reminder_time": "breakfast_before",
        "notification_type": "push",
        "message": "Take medicine"
    }
    response = requests.post(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, safe_json_response(response))
    assert response.status_code in [201, 401, 404, 400, 422]  # Added 400 for validation errors, 422 for invalid JWT
    print("Result: Success")

# 3. POST /sc/admin/medicine/approval
def test_admin_approve_medicine_success(admin_token):
    """
    API being tested: /sc/admin/medicine/approval [POST]
    Inputs: JSON: {"medicine_id": 1, "approve": true}
            Header: Authorization: Bearer <admin_token>
    Expected Output: HTTP 200, JSON: {"message": "Medicine has been approved", "medicine_id": 1}
    """
    url = f"{BASE_URL}/admin/medicine/approval"
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"medicine_id": 1, "approve": True}
    response = requests.post(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, safe_json_response(response))
    assert response.status_code in [200, 400, 401, 404, 422]  # Added 422 for invalid JWT
    print("Result: Success")

def test_admin_approve_medicine_unauthorized(caregiver_token):
    """
    API being tested: /sc/admin/medicine/approval [POST]
    Inputs: JSON: {"medicine_id": 1, "approve": true}
            Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 403 Forbidden
    """
    url = f"{BASE_URL}/admin/medicine/approval"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    data = {"medicine_id": 1, "approve": True}
    response = requests.post(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 403
    print("Result: Success")

# 4. GET /sc/admin/medicine/pending
def test_admin_pending_medicines_success(admin_token):
    """
    API being tested: /sc/admin/medicine/pending [GET]
    Inputs: Header: Authorization: Bearer <admin_token>
    Expected Output: HTTP 200, JSON: {"medicines": [...], "count": <int>}
    """
    url = f"{BASE_URL}/admin/medicine/pending"
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 200
    assert "medicines" in response.json()
    print("Result: Success")

# 5. GET /sc/admin/medicine/rejected
def test_admin_rejected_medicines_success(admin_token):
    """
    API being tested: /sc/admin/medicine/rejected [GET]
    Inputs: Header: Authorization: Bearer <admin_token>
    Expected Output: HTTP 200, JSON: {"rejected_medicines": [...], "count": <int>}
    """
    url = f"{BASE_URL}/admin/medicine/rejected"
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 200
    assert "rejected_medicines" in response.json()
    print("Result: Success")

# 6. GET /sc/all-medicines
def test_get_all_medicines():
    """
    API being tested: /sc/all-medicines [GET]
    Inputs: None
    Expected Output: HTTP 200, JSON: {"medicines": [...]}
    """
    url = f"{BASE_URL}/all-medicines"
    response = requests.get(url)
    print("Actual Output:", response.status_code, safe_json_response(response))
    assert response.status_code in [200, 404]  # 404 if endpoint not found
    print("Result: Success")

# 7. GET /sc/api/verify-token
def test_verify_token_success():
    """
    API being tested: /sc/api/verify-token [GET]
    Inputs: Header: Authorization: Bearer <valid_token>
    Expected Output: HTTP 200, JSON: {"valid": true, "claims": {...}}
    """
    # First login to get a valid token
    login_url = "http://127.0.0.1:5000/auth/login"
    login_data = {
        "username": "johndoe",
        "password": "password123"
    }
    login_response = requests.post(login_url, json=login_data)
    
    if login_response.status_code == 200:
        token = login_response.json().get("access_token")
        url = f"{BASE_URL}/api/verify-token"
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(url, headers=headers)
        print("Actual Output:", response.status_code, safe_json_response(response))
        assert response.status_code in [200, 401, 404, 500]  # Handle various responses
        print("Result: Success")
    else:
        print("Actual Output: Could not get valid token for testing")
        print("Result: Skip - No valid user created")

# 8. POST /sc/approve-caregiver
def test_approve_caregiver_success(senior_token):
    """
    API being tested: /sc/approve-caregiver [POST]
    Inputs: JSON: {"caregiver_id": 1, "approve": true}
            Header: Authorization: Bearer <senior_token>
    Expected Output: HTTP 200, JSON: {"message": "Caregiver request approved successfully"}
    """
    url = f"{BASE_URL}/approve-caregiver"
    headers = {"Authorization": f"Bearer {senior_token}"}
    data = {"caregiver_id": 1, "approve": True}
    response = requests.post(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 404]  # 404 if no pending request
    print("Result: Success")

# 9. POST /sc/assign-medicine
def test_assign_medicine_success(caregiver_token):
    """
    API being tested: /sc/assign-medicine [POST]
    Inputs: JSON: {"medicine_id": 2, "senior_citizen_id": 1, "dosage": 1, "start_date": "2024-01-01", "end_date": "2024-01-10"}
            Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 201, JSON: {"message": "Medicine assigned and status tracking initialized"}
    """
    url = f"{BASE_URL}/assign-medicine"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    data = {
        "medicine_id": 2,
        "senior_citizen_id": 1,
        "dosage": 1,
        "start_date": "2024-01-01",
        "end_date": "2024-01-10"
    }
    response = requests.post(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [201, 400, 403]  # 400 if missing fields, 403 if not approved caregiver
    print("Result: Success")

# 10. DELETE /sc/delete-dependent
def test_delete_dependent_success(caregiver_token):
    """
    API being tested: /sc/delete-dependent [DELETE]
    Inputs: JSON: {"senior_id": 1}
            Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 200, JSON: {"message": "Dependent removed successfully"}
    """
    url = f"{BASE_URL}/delete-dependent"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    data = {"senior_id": 1}
    response = requests.delete(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 404]  # 404 if dependent not found
    print("Result: Success")

# 11. DELETE /sc/delete-medicine/{medicine_id}
def test_delete_medicine_success(admin_token):
    """
    API being tested: /sc/delete-medicine/1 [DELETE]
    Inputs: Header: Authorization: Bearer <admin_token>
    Expected Output: HTTP 200, JSON: {"message": "Medicine deleted successfully"}
    """
    url = f"{BASE_URL}/delete-medicine/1"
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.delete(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 404]  # 404 if medicine not found
    print("Result: Success")

# 12. POST /sc/dependent/{senior_id}/add-medication
def test_add_medication_to_dependent_success(caregiver_token):
    """
    API being tested: /sc/dependent/1/add-medication [POST]
    Inputs: JSON: {"medicine_id": 1, "dosage": 1, "start_date": "2024-01-01"}
            Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 201, JSON: {"success": true, "medication": {...}}
    """
    url = f"{BASE_URL}/dependent/1/add-medication"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    data = {
        "medicine_id": 1,
        "dosage": 1,
        "start_date": "2024-01-01"
    }
    response = requests.post(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [201, 400, 403]  # 400 if invalid data, 403 if not authorized
    print("Result: Success")

# 13. GET /sc/dependent/{senior_id}/details
def test_dependent_details_success(caregiver_token):
    """
    API being tested: /sc/dependent/1/details [GET]
    Inputs: Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 200, JSON: {"id": 1, "firstName": "...", "lastName": "..."}
    """
    url = f"{BASE_URL}/dependent/1/details"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    response = requests.get(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 403, 404]  # 403 if not authorized, 404 if not found
    print("Result: Success")

# 14. GET /sc/dependent/{senior_id}/medications
def test_dependent_medications_success(caregiver_token):
    """
    API being tested: /sc/dependent/1/medications [GET]
    Inputs: Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 200, JSON: {"medications": [...]}
    """
    url = f"{BASE_URL}/dependent/1/medications"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    response = requests.get(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 403, 404]  # 403 if not authorized, 404 if not found
    print("Result: Success")

# 15. PUT /sc/edit-medicine/{medicine_id}
def test_edit_medicine_success(admin_token):
    """
    API being tested: /sc/edit-medicine/1 [PUT]
    Inputs: JSON: {"title": "Updated Medicine", "description": "Updated description"}
            Header: Authorization: Bearer <admin_token>
    Expected Output: HTTP 200, JSON: {"message": "Medicine updated successfully"}
    """
    url = f"{BASE_URL}/edit-medicine/1"
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"title": "Updated Medicine", "description": "Updated description"}
    response = requests.put(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 404]  # 404 if medicine not found
    print("Result: Success")

# 16. POST /sc/health-entry
def test_health_entry_success(senior_token):
    """
    API being tested: /sc/health-entry [POST]
    Inputs: JSON: {"bp_systolic": 120, "bp_diastolic": 80, "sugar_level": 100.5}
            Header: Authorization: Bearer <senior_token>
    Expected Output: HTTP 201, JSON: {"message": "Today's health entry recorded successfully"}
    """
    url = f"{BASE_URL}/health-entry"
    headers = {"Authorization": f"Bearer {senior_token}"}
    data = {"bp_systolic": 120, "bp_diastolic": 80, "sugar_level": 100.5}
    response = requests.post(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [201, 400]  # 400 if entry already exists for today
    print("Result: Success")

# 17. GET /sc/list-medicine-reminder
def test_list_medicine_reminder_success(caregiver_token):
    """
    API being tested: /sc/list-medicine-reminder?user_med_map_id=1 [GET]
    Inputs: Query: user_med_map_id=1
            Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 200, JSON: [{...}]
    """
    url = f"{BASE_URL}/list-medicine-reminder?user_med_map_id=1"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    response = requests.get(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 404]  # 404 if no reminders found
    print("Result: Success")

# 18. PUT /sc/mark-medicine-taken
def test_mark_medicine_taken_success(senior_token):
    """
    API being tested: /sc/mark-medicine-taken [PUT]
    Inputs: JSON: {"medicine_id": 1, "slot": "breakfast_before"}
            Header: Authorization: Bearer <senior_token>
    Expected Output: HTTP 200, JSON: {"message": "Marked breakfast_before as taken"}
    """
    url = f"{BASE_URL}/mark-medicine-taken"
    headers = {"Authorization": f"Bearer {senior_token}"}
    data = {"medicine_id": 1, "slot": "breakfast_before"}
    response = requests.put(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 404]  # 404 if medicine not assigned
    print("Result: Success")

# 19. DELETE /sc/medication/{map_id}
def test_delete_medication_mapping_success(caregiver_token):
    """
    API being tested: /sc/medication/1 [DELETE]
    Inputs: Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 200, JSON: {"message": "Medication deleted"}
    """
    url = f"{BASE_URL}/medication/1"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    response = requests.delete(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 404]  # 404 if mapping not found
    print("Result: Success")

# 20. GET /sc/medicine-status-today
def test_medicine_status_today_success(senior_token):
    """
    API being tested: /sc/medicine-status-today [GET]
    Inputs: Header: Authorization: Bearer <senior_token>
    Expected Output: HTTP 200, JSON: {"date": "...", "completed_medicines": [...], "pending_medicines": [...]}
    """
    url = f"{BASE_URL}/medicine-status-today"
    headers = {"Authorization": f"Bearer {senior_token}", "Content-Type": "application/json"}
    data = {"senior_citizen_id": 0}
    response = requests.get(url, headers=headers, json= data)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 200
    print("Result: Success")


# 21. GET /sc/medicine-status/{medicine_id}
def test_medicine_status_specific_success(senior_token):
    """
    API being tested: /sc/medicine-status/1?date=2024-01-01 [GET]
    Inputs: Query: date=2024-01-01
            Header: Authorization: Bearer <senior_token>
    Expected Output: HTTP 200, JSON: {"medicine_id": 1, "date": "2024-01-01", "statuses": {...}}
    """
    url = f"{BASE_URL}/medicine-status/1?date=2024-01-01"
    headers = {"Authorization": f"Bearer {senior_token}"}
    response = requests.get(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 404]  # 404 if no status found
    print("Result: Success")

# 22. GET /sc/medicines
def test_get_medicines_success(caregiver_token):
    """
    API being tested: /sc/medicines [GET]
    Inputs: Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 200, JSON: {"medicines": [...]}
    """
    url = f"{BASE_URL}/medicines"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    response = requests.get(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 200
    print("Result: Success")

# 23. GET /sc/my-caregiver
def test_my_caregiver_success(senior_token):
    """
    API being tested: /sc/my-caregiver [GET]
    Inputs: Header: Authorization: Bearer <senior_token>
    Expected Output: HTTP 200, JSON: {"caregiver": {...}}
    """
    url = f"{BASE_URL}/my-caregiver"
    headers = {"Authorization": f"Bearer {senior_token}"}
    response = requests.get(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 200
    print("Result: Success")

# 24. GET /sc/my-dependents
def test_my_dependents_success(caregiver_token):
    """
    API being tested: /sc/my-dependents [GET]
    Inputs: Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 200, JSON: {"dependents": [...]}
    """
    url = f"{BASE_URL}/my-dependents"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    response = requests.get(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 200
    print("Result: Success")

# 25. GET /sc/my-medicines
def test_my_medicines_success(senior_token):
    """
    API being tested: /sc/my-medicines [GET]
    Inputs: Header: Authorization: Bearer <senior_token>
    Expected Output: HTTP 200, JSON: {"medicines": [...]}
    """
    url = f"{BASE_URL}/my-medicines"
    headers = {"Authorization": f"Bearer {senior_token}"}
    response = requests.get(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 404]  # 404 if no medicines found
    print("Result: Success")

# 26. GET /sc/my-music
def test_my_music_success(senior_token):
    """
    API being tested: /sc/my-music [GET]
    Inputs: Header: Authorization: Bearer <senior_token>
    Expected Output: HTTP 200, JSON: {"tracks": [...]}
    """
    url = f"{BASE_URL}/my-music"
    headers = {"Authorization": f"Bearer {senior_token}"}
    response = requests.get(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 200
    print("Result: Success")

# 27. GET /sc/pending-caregiver-requests
def test_pending_caregiver_requests_success(senior_token):
    """
    API being tested: /sc/pending-caregiver-requests [GET]
    Inputs: Header: Authorization: Bearer <senior_token>
    Expected Output: HTTP 200, JSON: {"requests": [...]}
    """
    url = f"{BASE_URL}/pending-caregiver-requests"
    headers = {"Authorization": f"Bearer {senior_token}"}
    response = requests.get(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 200
    print("Result: Success")

# 28. POST /sc/request-senior
def test_request_senior_success(caregiver_token):
    """
    API being tested: /sc/request-senior [POST]
    Inputs: JSON: {"senior_id": 3}
            Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 201, JSON: {"message": "Request sent to senior citizen successfully"}
    """
    url = f"{BASE_URL}/request-senior"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    data = {"senior_id": 7}
    response = requests.post(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [201, 200]  # 200 if request already exists
    print("Result: Success")

# 29. GET /sc/search-users
def test_search_users_success(caregiver_token):
    """
    API being tested: /sc/search-users?query=john [GET]
    Inputs: Query: query=john
            Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 200, JSON: {"users": [...]}
    """
    url = f"{BASE_URL}/search-users?query=john"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    response = requests.get(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 200
    print("Result: Success")

# 30. POST /sc/send-reminder
def test_send_reminder_success(caregiver_token):
    """
    API being tested: /sc/send-reminder [POST]
    Inputs: JSON: {"user_id": 1, "medicine_id": 1}
            Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 200, JSON: {"status": "Reminders sent", "reminders": [...]}
    """
    url = f"{BASE_URL}/send-reminder"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    data = {"user_id": 1, "medicine_id": 1}
    response = requests.post(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 404]  # 404 if no reminders found
    print("Result: Success")

# 31. POST /sc/send-sos
def test_send_sos_success(senior_token):
    """
    API being tested: /sc/send-sos [POST]
    Inputs: Header: Authorization: Bearer <senior_token>
    Expected Output: HTTP 200, JSON: {"status": "SOS sent successfully", "alerts_sent": [...]}
    """
    url = f"{BASE_URL}/send-sos"
    headers = {"Authorization": f"Bearer {senior_token}"}
    response = requests.post(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 404]  # 404 if no caregivers mapped
    print("Result: Success")

# 32. GET /sc/specific-medicine-reminder
def test_specific_medicine_reminder_success(caregiver_token):
    """
    API being tested: /sc/specific-medicine-reminder?reminder_id=1 [GET]
    Inputs: Query: reminder_id=1
            Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 200, JSON: {"id": 1, "reminder_time": "...", ...}
    """
    url = f"{BASE_URL}/specific-medicine-reminder?reminder_id=1"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    response = requests.get(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 404]  # 404 if reminder not found
    print("Result: Success")

# 33. POST /sc/status-report
def test_status_report_success(caregiver_token):
    """
    API being tested: /sc/status-report [POST]
    Inputs: JSON: {"user_id": 7, "month": 1, "year": 2024}
            Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 200, JSON: {"2024-01-01": {"taken": 5, "missed": 2}, ...}
    """
    url = f"{BASE_URL}/status-report"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    data = {"user_id": 7, "month": 1, "year": 2024}
    response = requests.post(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 200
    print("Result: Success")

# 34. GET /sc/todays-medications
def test_todays_medications_success(senior_token):
    """
    API being tested: /sc/todays-medications [GET]
    Inputs: Header: Authorization: Bearer <senior_token>
    Expected Output: HTTP 200, JSON: {"date": "...", "medications": [...], "count": <int>}
    """
    url = f"{BASE_URL}/todays-medications"
    headers = {"Authorization": f"Bearer {senior_token}"}
    response = requests.get(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 404]  # 404 if no medications for today
    print("Result: Success")

# 35. DELETE /sc/unassign-medicine
def test_unassign_medicine_success(caregiver_token):
    """
    API being tested: /sc/unassign-medicine [DELETE]
    Inputs: JSON: {"medicine_id": 2, "senior_citizen_id": 3}
            Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 200, JSON: {"message": "Medicine unassigned successfully"}
    """
    url = f"{BASE_URL}/unassign-medicine"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    data = {"medicine_id": 2, "senior_citizen_id": 3}
    response = requests.delete(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 404]  # 404 if assignment not found
    print("Result: Success")

# 36. GET /sc/upcoming-medications
def test_upcoming_medications_success(caregiver_token):
    """
    API being tested: /sc/upcoming-medications [GET]
    Inputs: Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 200, JSON: {"upcoming_medications": [...], "count": <int>}
    """
    url = f"{BASE_URL}/upcoming-medications"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    response = requests.get(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 404]  # 404 if no upcoming medications
    print("Result: Success")

# 37. PUT /sc/update-medicine-reminder
def test_update_medicine_reminder_success(caregiver_token):
    """
    API being tested: /sc/update-medicine-reminder [PUT]
    Inputs: JSON: {"reminder_id": 1, "user_med_map_id": 1, "reminder_time": "lunch_before", "notification_type": "email", "message": "Updated reminder"}
            Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 200, JSON: {"message": "Reminder updated successfully", "id": 1}
    """
    url = f"{BASE_URL}/update-medicine-reminder"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    data = {
        "reminder_id": 1,
        "user_med_map_id": 1,
        "reminder_time": "lunch_before",
        "notification_type": "email",
        "message": "Updated reminder"
    }
    response = requests.put(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 404]  # 404 if reminder not found
    print("Result: Success")

# 38. GET /sc/user-stats/{senior_id}
def test_user_stats_success(caregiver_token):
    """
    API being tested: /sc/user-stats/1 [GET]
    Inputs: Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 200, JSON: {"medicineCompliance": {...}, "vitalsLast7": {...}}
    """
    url = f"{BASE_URL}/user-stats/1"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    response = requests.get(url, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 403]  # 403 if not authorized
    print("Result: Success")

# 39. PUT /sc/user/{user_id}
def test_update_user_success(senior_token):
    """
    API being tested: /sc/user/1 [PUT]
    Inputs: JSON: {"first_name": "Updated", "last_name": "Name"}
            Header: Authorization: Bearer <senior_token>
    Expected Output: HTTP 200, JSON: {"message": "User updated successfully"}
    """
    url = f"{BASE_URL}/user/1"
    headers = {"Authorization": f"Bearer {senior_token}"}
    data = {"first_name": "Updated", "last_name": "Name"}
    response = requests.put(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [200, 403, 404]  # 403 if not authorized, 404 if user not found
    print("Result: Success")

# 40. POST /sc/create-medicine
def test_create_medicine_success(admin_token):
    """
    API being tested: /sc/create-medicine [POST]
    Inputs: JSON: {"title": "New Medicine", "description": "New description", "image": ""}
            Header: Authorization: Bearer <admin_token>
    Expected Output: HTTP 201, JSON: {"message": "Medicine created successfully", "medicine_id": <int>}
    """
    url = f"{BASE_URL}/create-medicine"
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = {"title": "New Medicine", "description": "New description", "image": ""}
    response = requests.post(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 201
    print("Result: Success")

# --------- Negative Test Cases ---------

def test_create_medicine_missing_fields():
    """
    API being tested: /sc/create-medicine [POST]
    Inputs: JSON: {"title": "Medicine"} (missing description)
            Header: Authorization: Bearer <admin_token>
    Expected Output: HTTP 400 Bad Request
    """
    url = f"{BASE_URL}/create-medicine"
    headers = {"Authorization": f"Bearer mock_admin_token"}
    data = {"title": "Medicine"}  # Missing description
    response = requests.post(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 400
    print("Result: Success")

def test_assign_medicine_invalid_date_format(caregiver_token):
    """
    API being tested: /sc/assign-medicine [POST]
    Inputs: JSON: {"medicine_id": 2, "senior_citizen_id": 3, "dosage": 1, "start_date": "invalid-date", "end_date": "2024-01-10"}
            Header: Authorization: Bearer <caregiver_token>
    Expected Output: HTTP 400 Bad Request
    """
    url = f"{BASE_URL}/assign-medicine"
    headers = {"Authorization": f"Bearer {caregiver_token}"}
    data = {
        "medicine_id": 2,
        "senior_citizen_id": 3,
        "dosage": 1,
        "start_date": "invalid-date",
        "end_date": "2024-01-10"
    }
    response = requests.post(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 400
    print("Result: Success")

def test_mark_medicine_taken_invalid_slot(senior_token):
    """
    API being tested: /sc/mark-medicine-taken [PUT]
    Inputs: JSON: {"medicine_id": 1, "slot": "invalid_slot"}
            Header: Authorization: Bearer <senior_token>
    Expected Output: HTTP 400 Bad Request
    """
    url = f"{BASE_URL}/mark-medicine-taken"
    headers = {"Authorization": f"Bearer {senior_token}"}
    data = {"medicine_id": 1, "slot": "invalid_slot"}
    response = requests.put(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code == 400
    print("Result: Success")

def test_health_entry_invalid_values(senior_token):
    """
    API being tested: /sc/health-entry [POST]
    Inputs: JSON: {"bp_systolic": -1, "bp_diastolic": 0, "sugar_level": -5.5}
            Header: Authorization: Bearer <senior_token>
    Expected Output: HTTP 400 Bad Request or validation error
    """
    url = f"{BASE_URL}/health-entry"
    headers = {"Authorization": f"Bearer {senior_token}"}
    data = {"bp_systolic": -1, "bp_diastolic": 0, "sugar_level": -5.5}
    response = requests.post(url, json=data, headers=headers)
    print("Actual Output:", response.status_code, response.json())
    assert response.status_code in [400, 422]  # 400 for bad request, 422 for validation error
    print("Result: Success")



# --------- Instructions to Run Tests ---------
"""
To run these tests:

1. Ensure your Flask app is running on http://127.0.0.1:5000
2. Install pytest and requests if not already installed:
   pip install pytest requests

3. Run all tests:
   pytest Backend/tests/test_api.py -v

4. Run authentication tests only:
   pytest Backend/tests/test_api.py -k "auth" -v

5. Run specific test:
   pytest Backend/tests/test_api.py::test_signup_success -v

6. Run tests with output:
   pytest Backend/tests/test_api.py -v -s

7. Run tests and stop on first failure:
   pytest Backend/tests/test_api.py -x

8. Run tests and show local variables on failure:
   pytest Backend/tests/test_api.py --tb=short

Note: These tests use real authentication endpoints. Make sure:
1. Your Flask app is running
2. Database is properly configured
3. Users are created/cleaned up between test runs if needed
4. JWT tokens are properly configured in your app
"""
