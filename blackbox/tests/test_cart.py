import pytest
import requests
from conftest import BASE_URL, API_PATH, get_headers


class TestCart:

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        headers = get_headers()
        requests.delete(f"{BASE_URL}{API_PATH}/cart/clear", headers=headers)
        yield
        requests.delete(f"{BASE_URL}{API_PATH}/cart/clear", headers=headers)

    def test_get_empty_cart(self):
        headers = get_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/cart", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_add_item_to_cart_valid(self):
        headers = get_headers()
        payload = {"product_id": 1, "quantity": 1}
        response = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                headers=headers, json=payload)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"

    def test_add_item_quantity_zero(self):
        headers = get_headers()
        payload = {"product_id": 1, "quantity": 0}
        response = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_add_item_negative_quantity(self):
        headers = get_headers()
        payload = {"product_id": 1, "quantity": -5}
        response = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_add_non_existent_product(self):
        headers = get_headers()
        payload = {"product_id": 99999, "quantity": 1}
        response = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                headers=headers, json=payload)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    def test_add_item_exceeding_stock(self):
        headers = get_headers()
        add_payload = {"product_id": 1, "quantity": 200}
        response = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                headers=headers, json=add_payload)
        assert response.status_code == 400, f"Expected 400 for exceeding stock, got {response.status_code}"

    def test_add_same_product_twice_quantity_addition(self):
        headers = get_headers()
        payload1 = {"product_id": 1, "quantity": 2}
        response1 = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                 headers=headers, json=payload1)
        if response1.status_code in [200, 201]:
            payload2 = {"product_id": 1, "quantity": 3}
            response2 = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                     headers=headers, json=payload2)
            assert response2.status_code in [200, 201]

            cart_response = requests.get(f"{BASE_URL}{API_PATH}/cart", headers=headers)
            if cart_response.status_code == 200:
                cart_data = cart_response.json()
                items = cart_data.get("items", [])
                for item in items:
                    if item.get("product_id") == 1:
                        assert item.get("quantity") == 5, \
                            f"Expected quantity 5 (2+3), got {item.get('quantity')}"
                        break

    def test_update_cart_item_valid_quantity(self):
        headers = get_headers()
        add_payload = {"product_id": 1, "quantity": 2}
        add_response = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                    headers=headers, json=add_payload)
        if add_response.status_code in [200, 201]:
            update_payload = {"product_id": 1, "quantity": 5}
            update_response = requests.post(f"{BASE_URL}{API_PATH}/cart/update",
                                           headers=headers, json=update_payload)
            assert update_response.status_code in [200, 201], f"Expected 200/201, got {update_response.status_code}"

    def test_update_cart_item_to_zero_quantity(self):
        headers = get_headers()
        add_payload = {"product_id": 1, "quantity": 2}
        add_response = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                    headers=headers, json=add_payload)
        if add_response.status_code in [200, 201]:
            update_payload = {"product_id": 1, "quantity": 0}
            update_response = requests.post(f"{BASE_URL}{API_PATH}/cart/update",
                                           headers=headers, json=update_payload)
            assert update_response.status_code == 400, f"Expected 400, got {update_response.status_code}"

    def test_update_non_existent_cart_item(self):
        headers = get_headers()
        payload = {"product_id": 99999, "quantity": 5}
        response = requests.post(f"{BASE_URL}{API_PATH}/cart/update",
                                headers=headers, json=payload)
        assert response.status_code in [400, 404], f"Expected 400/404, got {response.status_code}"

    def test_remove_item_from_cart(self):
        headers = get_headers()
        add_payload = {"product_id": 1, "quantity": 2}
        add_response = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                    headers=headers, json=add_payload)
        if add_response.status_code in [200, 201]:
            remove_payload = {"product_id": 1}
            remove_response = requests.post(f"{BASE_URL}{API_PATH}/cart/remove",
                                           headers=headers, json=remove_payload)
            assert remove_response.status_code in [200, 201], f"Expected 200/201, got {remove_response.status_code}"

    def test_remove_non_existent_cart_item(self):
        headers = get_headers()
        payload = {"product_id": 99999}
        response = requests.post(f"{BASE_URL}{API_PATH}/cart/remove",
                                headers=headers, json=payload)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    def test_clear_cart(self):
        headers = get_headers()
        response = requests.delete(f"{BASE_URL}{API_PATH}/cart/clear", headers=headers)
        assert response.status_code in [200, 204], f"Expected 200/204, got {response.status_code}"

    def test_verify_item_subtotal_calculation(self):
        headers = get_headers()
        add_payload = {"product_id": 1, "quantity": 3}
        add_response = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                    headers=headers, json=add_payload)
        if add_response.status_code in [200, 201]:
            cart_response = requests.get(f"{BASE_URL}{API_PATH}/cart", headers=headers)
            if cart_response.status_code == 200:
                cart_data = cart_response.json()
                if isinstance(cart_data, dict) and "items" in cart_data:
                    items = cart_data["items"]
                    if len(items) > 0:
                        item = items[0]
                        subtotal = item.get("subtotal", 0)
                        quantity = item.get("quantity", 0)
                        price = item.get("price") or item.get("unit_price", 0)
                        assert abs(subtotal - quantity * price) < 0.01, \
                            f"Subtotal {subtotal} != {quantity} * {price}"

    def test_verify_cart_total_includes_all_items(self):
        headers = get_headers()
        add_payload1 = {"product_id": 1, "quantity": 2}
        requests.post(f"{BASE_URL}{API_PATH}/cart/add", headers=headers, json=add_payload1)
        add_payload2 = {"product_id": 2, "quantity": 1}
        requests.post(f"{BASE_URL}{API_PATH}/cart/add", headers=headers, json=add_payload2)

        cart_response = requests.get(f"{BASE_URL}{API_PATH}/cart", headers=headers)
        if cart_response.status_code == 200:
            cart_data = cart_response.json()
            if isinstance(cart_data, dict) and "items" in cart_data:
                items = cart_data["items"]
                total_from_items = sum(item.get("subtotal", 0) for item in items)
                cart_total = cart_data.get("total", 0)
                assert abs(cart_total - total_from_items) < 0.01, \
                    f"Cart total {cart_total} != sum of subtotals {total_from_items}"

    def test_cart_total_cannot_be_negative(self):
        headers = get_headers()
        add_payload = {"product_id": 1, "quantity": 1}
        requests.post(f"{BASE_URL}{API_PATH}/cart/add", headers=headers, json=add_payload)
        payload = {"coupon_code": "WELCOME50"}
        requests.post(f"{BASE_URL}{API_PATH}/coupon/apply", headers=headers, json=payload)
        cart_response = requests.get(f"{BASE_URL}{API_PATH}/cart", headers=headers)
        cart_data = cart_response.json()
        total = cart_data.get("total", 0)
        assert total >= 0, f"Expected total to be non-negative, got {total}"
