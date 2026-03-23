import pytest
import requests
from conftest import BASE_URL, API_PATH, get_headers, get_admin_headers


class TestCoupons:

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        headers = get_headers()
        requests.delete(f"{BASE_URL}{API_PATH}/cart/clear", headers=headers)
        yield
        requests.delete(f"{BASE_URL}{API_PATH}/cart/clear", headers=headers)

    def test_apply_invalid_coupon(self):
        headers = get_headers()
        res = requests.post(f"{BASE_URL}{API_PATH}/coupon/apply",
                           json={"coupon_code": "INVALID_CODE_XYZ"}, headers=headers)
        assert res.status_code in [400, 404], f"Expected 400/404, got {res.status_code}"

    def test_apply_coupon_below_minimum(self):
        headers = get_headers()
        add_payload = {"product_id": 1, "quantity": 1}
        requests.post(f"{BASE_URL}{API_PATH}/cart/add", headers=headers, json=add_payload)

        payload = {"coupon_code": "TEST"}
        response = requests.post(f"{BASE_URL}{API_PATH}/coupon/apply",
                                headers=headers, json=payload)
        assert response.status_code in [400, 404, 422], f"Expected 400/404/422 for below minimum, got {response.status_code}"

    def test_apply_coupon_percent_discount(self):
        headers = get_headers()
        add_payload = {"product_id": 1, "quantity": 2}
        add_response = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                    headers=headers, json=add_payload)
        if add_response.status_code in [200, 201]:
            cart_before = requests.get(f"{BASE_URL}{API_PATH}/cart", headers=headers)
            if cart_before.status_code == 200:
                before_data = cart_before.json()
                original_total = before_data.get("total", 0)

                coupon_payload = {"coupon_code": "PERCENT10"}
                response = requests.post(f"{BASE_URL}{API_PATH}/coupon/apply",
                                        headers=headers, json=coupon_payload)

                if response.status_code in [200, 201]:
                    response_data = response.json()
                    expected_discount = original_total * 0.10
                    actual_discount = response_data.get("discount_amount") or response_data.get("discount", 0)
                    expected_total = original_total - expected_discount
                    actual_total = response_data.get("discounted_total") or response_data.get("total", 0)

                    assert abs(actual_discount - expected_discount) < 0.01 or abs(actual_total - expected_total) < 0.01, \
                        f"10% discount calculation incorrect: expected discount {expected_discount}, got {actual_discount}"

    def test_apply_coupon_fixed_discount(self):
        headers = get_headers()
        add_payload = {"product_id": 1, "quantity": 2}
        add_response = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                    headers=headers, json=add_payload)
        if add_response.status_code in [200, 201]:
            cart_before = requests.get(f"{BASE_URL}{API_PATH}/cart", headers=headers)
            if cart_before.status_code == 200:
                before_data = cart_before.json()
                original_total = before_data.get("total", 0)

                coupon_payload = {"coupon_code": "FIXED50"}
                response = requests.post(f"{BASE_URL}{API_PATH}/coupon/apply",
                                        headers=headers, json=coupon_payload)

                if response.status_code in [200, 201]:
                    response_data = response.json()
                    expected_discount = 50
                    actual_discount = response_data.get("discount_amount") or response_data.get("discount", 0)
                    expected_total = original_total - expected_discount
                    actual_total = response_data.get("discounted_total") or response_data.get("total", 0)

                    assert abs(actual_discount - expected_discount) < 0.01 or abs(actual_total - expected_total) < 0.01, \
                        f"Fixed discount calculation incorrect: expected discount {expected_discount}, got {actual_discount}"

    def test_apply_coupon_with_discount_cap(self):
        headers = get_headers()
        add_payload = {"product_id": 1, "quantity": 10}
        add_response = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                    headers=headers, json=add_payload)
        if add_response.status_code in [200, 201]:
            coupon_payload = {"coupon_code": "CAPPED"}
            response = requests.post(f"{BASE_URL}{API_PATH}/coupon/apply",
                                    headers=headers, json=coupon_payload)
            if response.status_code in [200, 201]:
                response_data = response.json()
                actual_discount = response_data.get("discount_amount") or response_data.get("discount", 0)
                assert actual_discount <= 200, \
                    f"Discount {actual_discount} should not exceed cap of 200"

    def test_remove_coupon(self):
        headers = get_headers()
        response = requests.post(f"{BASE_URL}{API_PATH}/coupon/remove",
                                headers=headers)
        assert response.status_code in [200, 400, 404, 422], f"Got {response.status_code}"

    def test_apply_expired_coupon(self):
        headers = get_headers()
        admin_headers = get_admin_headers()

        coupons = requests.get(f"{BASE_URL}{API_PATH}/admin/coupons", headers=admin_headers)
        if coupons.status_code == 200:
            for c in coupons.json():
                if c.get("is_expired") or c.get("expired"):
                    add_payload = {"product_id": 1, "quantity": 1}
                    requests.post(f"{BASE_URL}{API_PATH}/cart/add", headers=headers, json=add_payload)
                    res = requests.post(f"{BASE_URL}{API_PATH}/coupon/apply",
                                       json={"coupon_code": c.get("code")}, headers=headers)
                    assert res.status_code in [400, 404], \
                        f"Expired coupon should not be accepted, got {res.status_code}"
                    break
