import pytest
import requests
from conftest import BASE_URL, API_PATH, get_headers, get_admin_headers

all_get_apis = [
    f"{BASE_URL+API_PATH}/admin/users",
    f"{BASE_URL+API_PATH}/admin/carts",
    f"{BASE_URL+API_PATH}/admin/orders",
    f"{BASE_URL+API_PATH}/admin/products",
    f"{BASE_URL+API_PATH}/admin/coupons",
    f"{BASE_URL+API_PATH}/admin/tickets",
    f"{BASE_URL+API_PATH}/admin/addresses",
    f"{BASE_URL+API_PATH}/profile",
    f"{BASE_URL+API_PATH}/addresses",
    f"{BASE_URL+API_PATH}/products",
    f"{BASE_URL+API_PATH}/cart",
    f"{BASE_URL+API_PATH}/wallet",
    f"{BASE_URL+API_PATH}/loyalty",
    f"{BASE_URL+API_PATH}/orders",
    f"{BASE_URL+API_PATH}/support/tickets",
]


class TestGlobalHeaderValidation:

    @pytest.mark.parametrize("endpoint", all_get_apis)
    def test_missing_roll_number_header(self, endpoint):
        headers = {"Content-Type": "application/json"}
        response = requests.get(endpoint, headers=headers)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.parametrize("endpoint", all_get_apis)
    def test_invalid_roll_number_non_integer(self, endpoint):
        headers = get_headers(roll_number="abc")
        response = requests.get(endpoint, headers=headers)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    @pytest.mark.parametrize("endpoint", all_get_apis)
    def test_invalid_user_id_non_integer(self, endpoint):
        headers = get_headers(user_id="abc")
        response = requests.get(endpoint, headers=headers)
        if "admin" in endpoint:
            assert True, "Admin endpoint - user ID not required"
        else:
            assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    @pytest.mark.parametrize("endpoint", all_get_apis)
    def test_missing_user_id_header(self, endpoint):
        headers = {
            "X-Roll-Number": "12345",
            "Content-Type": "application/json"
        }
        if "admin" in endpoint:
            assert True, "Admin endpoint - user ID not required"
        else:
            response = requests.get(endpoint, headers=headers)
            assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    @pytest.mark.parametrize("endpoint", all_get_apis)
    def test_invalid_user_id_negative(self, endpoint):
        headers = get_headers(user_id="-1")
        response = requests.get(endpoint, headers=headers)
        if "admin" in endpoint:
            assert True, "Admin endpoint - user ID not required"
        else:
            assert response.status_code == 400, f"Expected 400, got {response.status_code}"
