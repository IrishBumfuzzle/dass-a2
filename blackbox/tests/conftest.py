import pytest
import requests

BASE_URL = "http://localhost:8080"
API_PATH = "/api/v1"
VALID_ROLL_NUMBER = "12345"
VALID_USER_ID = "1"

def get_headers(user_id=VALID_USER_ID, roll_number=VALID_ROLL_NUMBER):
    return {
        "X-Roll-Number": roll_number,
        "X-User-ID": user_id,
        "Content-Type": "application/json"
    }

def get_admin_headers(roll_number=VALID_ROLL_NUMBER):
    return {
        "X-Roll-Number": roll_number,
        "Content-Type": "application/json"
    }

@pytest.fixture(scope="session")
def base_url():
    return BASE_URL + API_PATH

@pytest.fixture(scope="session")
def admin_headers():
    return get_admin_headers()

@pytest.fixture
def user_headers():
    return get_headers()
