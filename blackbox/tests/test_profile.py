import pytest
import requests
from conftest import BASE_URL, API_PATH, get_headers


class TestProfile:

    def test_get_profile(self):
        headers = get_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/profile", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "name" in data or "profile" in data

    def test_update_profile_valid(self):
        headers = get_headers()
        payload = {"name": "John Doe", "phone": "9876543210"}
        response = requests.put(f"{BASE_URL}{API_PATH}/profile",
                               headers=headers, json=payload)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"

    def test_update_profile_name_too_short(self):
        headers = get_headers()
        payload = {"name": "A", "phone": "9876543210"}
        response = requests.put(f"{BASE_URL}{API_PATH}/profile",
                               headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_update_profile_name_too_long(self):
        headers = get_headers()
        payload = {"name": "A" * 51, "phone": "9876543210"}
        response = requests.put(f"{BASE_URL}{API_PATH}/profile",
                               headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_update_profile_phone_9_digits(self):
        headers = get_headers()
        payload = {"name": "John Doe", "phone": "987654321"}
        response = requests.put(f"{BASE_URL}{API_PATH}/profile",
                               headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_update_profile_phone_11_digits(self):
        headers = get_headers()
        payload = {"name": "John Doe", "phone": "98765432100"}
        response = requests.put(f"{BASE_URL}{API_PATH}/profile",
                               headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_update_profile_non_numeric_phone(self):
        headers = get_headers()
        payload = {"name": "John Doe", "phone": "987654321a"}
        response = requests.put(f"{BASE_URL}{API_PATH}/profile",
                               headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_update_profile_name_boundary_2_chars(self):
        headers = get_headers()
        payload = {"name": "AB", "phone": "9876543210"}
        response = requests.put(f"{BASE_URL}{API_PATH}/profile",
                               headers=headers, json=payload)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"

    def test_update_profile_name_boundary_50_chars(self):
        headers = get_headers()
        payload = {"name": "A" * 50, "phone": "9876543210"}
        response = requests.put(f"{BASE_URL}{API_PATH}/profile",
                               headers=headers, json=payload)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
