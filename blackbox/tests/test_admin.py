import pytest
import requests
from conftest import BASE_URL, API_PATH, get_admin_headers


class TestAdminEndpoints:

    def test_admin_get_all_users(self):
        headers = get_admin_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/admin/users", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_admin_get_specific_user(self):
        headers = get_admin_headers()
        list_response = requests.get(f"{BASE_URL}{API_PATH}/admin/users", headers=headers)
        if list_response.status_code == 200:
            users = list_response.json()
            if isinstance(users, dict) and "users" in users:
                users = users["users"]
            if isinstance(users, list) and len(users) > 0:
                user_id = users[0].get("id") or users[0].get("user_id")
                response = requests.get(f"{BASE_URL}{API_PATH}/admin/users/{user_id}",
                                       headers=headers)
                assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_admin_get_all_carts(self):
        headers = get_admin_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/admin/carts", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_admin_get_all_orders(self):
        headers = get_admin_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/admin/orders", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_admin_get_all_products(self):
        headers = get_admin_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/admin/products", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_admin_get_all_coupons(self):
        headers = get_admin_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/admin/coupons", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_admin_get_all_tickets(self):
        headers = get_admin_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/admin/tickets", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_admin_get_all_addresses(self):
        headers = get_admin_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/admin/addresses", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_admin_no_user_id_required(self):
        headers = get_admin_headers()  # No X-User-ID
        endpoints = [
            f"{BASE_URL}{API_PATH}/admin/users",
            f"{BASE_URL}{API_PATH}/admin/carts",
            f"{BASE_URL}{API_PATH}/admin/orders",
            f"{BASE_URL}{API_PATH}/admin/products",
            f"{BASE_URL}{API_PATH}/admin/coupons",
            f"{BASE_URL}{API_PATH}/admin/tickets",
            f"{BASE_URL}{API_PATH}/admin/addresses",
        ]
        for endpoint in endpoints:
            response = requests.get(endpoint, headers=headers)
            assert response.status_code == 200, f"Admin endpoint {endpoint} should work without X-User-ID, got {response.status_code}"
