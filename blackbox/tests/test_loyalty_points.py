import pytest
import requests
from conftest import BASE_URL, API_PATH, get_headers


class TestLoyaltyPoints:

    def test_get_loyalty_points(self):
        headers = get_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/loyalty", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "points" in data or "balance" in data or "loyalty_points" in data

    def test_redeem_loyalty_points_valid(self):
        headers = get_headers()
        points_response = requests.get(f"{BASE_URL}{API_PATH}/loyalty", headers=headers)
        if points_response.status_code == 200:
            points_data = points_response.json()
            current_points = points_data.get("points") or points_data.get("balance") or points_data.get("loyalty_points") or 0
            if current_points >= 10:
                payload = {"amount": 10}
                response = requests.post(f"{BASE_URL}{API_PATH}/loyalty/redeem",
                                        headers=headers, json=payload)
                assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"

    def test_redeem_zero_points(self):
        headers = get_headers()
        payload = {"amount": 0}
        response = requests.post(f"{BASE_URL}{API_PATH}/loyalty/redeem",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_redeem_negative_points(self):
        headers = get_headers()
        payload = {"amount": -10}
        response = requests.post(f"{BASE_URL}{API_PATH}/loyalty/redeem",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_redeem_more_points_than_available(self):
        headers = get_headers()
        payload = {"amount": 999999}
        response = requests.post(f"{BASE_URL}{API_PATH}/loyalty/redeem",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
