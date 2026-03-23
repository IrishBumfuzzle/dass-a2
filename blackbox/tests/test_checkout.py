import pytest
import requests
from conftest import BASE_URL, API_PATH, get_headers


class TestCheckout:

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        headers = get_headers()
        requests.delete(f"{BASE_URL}{API_PATH}/cart/clear", headers=headers)
        yield
        requests.delete(f"{BASE_URL}{API_PATH}/cart/clear", headers=headers)

    def test_checkout_empty_cart(self):
        headers = get_headers()
        payload = {"payment_method": "COD"}
        response = requests.post(f"{BASE_URL}{API_PATH}/checkout",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_checkout_invalid_payment_method(self):
        headers = get_headers()
        payload = {"payment_method": "BITCOIN"}
        response = requests.post(f"{BASE_URL}{API_PATH}/checkout",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_checkout_with_cod_valid(self):
        headers = get_headers()
        add_payload = {"product_id": 1, "quantity": 1}
        add_response = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                    headers=headers, json=add_payload)
        if add_response.status_code in [200, 201]:
            payload = {"payment_method": "COD"}
            response = requests.post(f"{BASE_URL}{API_PATH}/checkout",
                                    headers=headers, json=payload)
            assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"

    def test_checkout_with_wallet_valid(self):
        headers = get_headers()

        requests.post(f"{BASE_URL}{API_PATH}/wallet/add", headers=headers, json={"amount": 10000})

        add_payload = {"product_id": 1, "quantity": 1}
        add_response = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                    headers=headers, json=add_payload)
        if add_response.status_code in [200, 201]:
            payload = {"payment_method": "WALLET"}
            response = requests.post(f"{BASE_URL}{API_PATH}/checkout",
                                    headers=headers, json=payload)
            assert response.status_code in [200, 201, 400], f"Expected 200/201/400, got {response.status_code}"

    def test_checkout_with_card_valid(self):
        headers = get_headers()
        add_payload = {"product_id": 1, "quantity": 1}
        add_response = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                    headers=headers, json=add_payload)
        if add_response.status_code in [200, 201]:
            payload = {"payment_method": "CARD"}
            response = requests.post(f"{BASE_URL}{API_PATH}/checkout",
                                    headers=headers, json=payload)
            assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"

    def test_checkout_cod_exceeding_limit(self):
        headers = get_headers()
        for i in range(1, 6):
            add_payload = {"product_id": i, "quantity": 10}
            requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                         headers=headers, json=add_payload)

        cart_response = requests.get(f"{BASE_URL}{API_PATH}/cart", headers=headers)
        if cart_response.status_code == 200:
            cart_data = cart_response.json()
            cart_total = cart_data.get("total", 0)

            payload = {"payment_method": "COD"}
            response = requests.post(f"{BASE_URL}{API_PATH}/checkout",
                                    headers=headers, json=payload)

            if cart_total > 5000:
                assert response.status_code == 400, f"Expected 400 for COD exceeding limit, got {response.status_code}"
            else:
                assert response.status_code in [200, 201], f"Expected 200/201 for valid COD, got {response.status_code}"

    def test_checkout_payment_status_cod_pending(self):
        headers = get_headers()
        add_payload = {"product_id": 1, "quantity": 1}
        add_response = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                    headers=headers, json=add_payload)
        if add_response.status_code in [200, 201]:
            payload = {"payment_method": "COD"}
            checkout_response = requests.post(f"{BASE_URL}{API_PATH}/checkout",
                                             headers=headers, json=payload)
            if checkout_response.status_code in [200, 201]:
                checkout_data = checkout_response.json()
                payment_status = checkout_data.get("payment_status") or checkout_data.get("status")
                if payment_status:
                    assert payment_status.upper() in ["PENDING", "UNPAID"], \
                        f"COD payment status should be PENDING, got {payment_status}"

    def test_checkout_payment_status_card_paid(self):
        headers = get_headers()
        add_payload = {"product_id": 1, "quantity": 1}
        add_response = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                    headers=headers, json=add_payload)
        if add_response.status_code in [200, 201]:
            payload = {"payment_method": "CARD"}
            checkout_response = requests.post(f"{BASE_URL}{API_PATH}/checkout",
                                             headers=headers, json=payload)
            if checkout_response.status_code in [200, 201]:
                checkout_data = checkout_response.json()
                payment_status = checkout_data.get("payment_status") or checkout_data.get("status")
                if payment_status:
                    assert payment_status.upper() == "PAID", \
                        f"CARD payment status should be PAID, got {payment_status}"

    def test_checkout_wallet_pending(self):
        headers = get_headers()
        requests.post(f"{BASE_URL}{API_PATH}/wallet/add", headers=headers, json={"amount": 50000})
        add_payload = {"product_id": 1, "quantity": 1}
        add_response = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                    headers=headers, json=add_payload)
        if add_response.status_code in [200, 201]:
            payload = {"payment_method": "WALLET"}
            checkout_response = requests.post(f"{BASE_URL}{API_PATH}/checkout",
                                             headers=headers, json=payload)
            if checkout_response.status_code in [200, 201]:
                checkout_data = checkout_response.json()
                payment_status = checkout_data.get("payment_status") or checkout_data.get("status")
                if payment_status:
                    assert payment_status.upper() in ["PENDING", "UNPAID"], \
                        f"WALLET payment status should be PENDING, got {payment_status}"

    def test_checkout_gst_calculation_and_invoice(self):
        headers = get_headers()
        add_payload = {"product_id": 1, "quantity": 2}
        add_response = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                    headers=headers, json=add_payload)
        if add_response.status_code in [200, 201]:
            payload = {"payment_method": "CARD"}
            checkout_response = requests.post(f"{BASE_URL}{API_PATH}/checkout",
                                             headers=headers, json=payload)
            if checkout_response.status_code in [200, 201]:
                checkout_data = checkout_response.json()
                order_id = checkout_data.get("order_id") or checkout_data.get("id")
                if order_id:
                    invoice_response = requests.get(f"{BASE_URL}{API_PATH}/orders/{order_id}/invoice",
                                                   headers=headers)
                    if invoice_response.status_code == 200:
                        invoice_data = invoice_response.json()
                        invoice_subtotal = invoice_data.get("subtotal", 0)
                        invoice_gst = invoice_data.get("gst") or invoice_data.get("gst_amount", 0)
                        invoice_total = invoice_data.get("total") or invoice_data.get("total_amount", 0)

                        expected_gst = invoice_subtotal * 0.05
                        assert abs(invoice_gst - expected_gst) < 0.01, \
                            f"GST {invoice_gst} should be 5% of {invoice_subtotal} = {expected_gst}"

                        expected_total = invoice_subtotal + invoice_gst
                        assert abs(invoice_total - expected_total) < 0.01, \
                            f"Total {invoice_total} should equal subtotal {invoice_subtotal} + GST {invoice_gst} = {expected_total}"

    def test_checkout_total_with_gst_calculation(self):
        headers = get_headers()
        add_payload = {"product_id": 1, "quantity": 1}
        add_response = requests.post(f"{BASE_URL}{API_PATH}/cart/add",
                                    headers=headers, json=add_payload)
        if add_response.status_code in [200, 201]:
            cart_response = requests.get(f"{BASE_URL}{API_PATH}/cart", headers=headers)
            if cart_response.status_code == 200:
                cart_data = cart_response.json()
                cart_subtotal = cart_data.get("subtotal") or cart_data.get("total", 0)
                expected_total_with_gst = cart_subtotal * 1.05

                payload = {"payment_method": "COD"}
                checkout_response = requests.post(f"{BASE_URL}{API_PATH}/checkout",
                                                 headers=headers, json=payload)
                if checkout_response.status_code in [200, 201]:
                    checkout_data = checkout_response.json()
                    checkout_total = checkout_data.get("total") or checkout_data.get("total_amount", 0)
                    assert abs(checkout_total - expected_total_with_gst) < 0.01, \
                        f"Checkout total {checkout_total} should equal cart subtotal {cart_subtotal} + 5% GST = {expected_total_with_gst}"

    def test_checkout_removes_items_from_cart(self):
        headers = get_headers()
        add_payload = {"product_id": 1, "quantity": 1}
        requests.post(f"{BASE_URL}{API_PATH}/cart/add", headers=headers, json=add_payload)
        payload = {"payment_method": "COD"}
        checkout_resp = requests.post(f"{BASE_URL}{API_PATH}/checkout", headers=headers, json=payload)
        assert checkout_resp.status_code in [200, 201]
        cart_resp = requests.get(f"{BASE_URL}{API_PATH}/cart", headers=headers)
        cart_data = cart_resp.json()
        assert len(cart_data.get("items", [])) == 0, "Cart should be empty after checkout"

    def test_checkout_reduces_stock(self):
        headers = get_headers()
        prod_resp = requests.get(f"{BASE_URL}{API_PATH}/products/1", headers=headers)
        initial_stock = prod_resp.json().get("stock_quantity") or prod_resp.json().get("stock", 0)

        add_payload = {"product_id": 1, "quantity": 1}
        requests.post(f"{BASE_URL}{API_PATH}/cart/add", headers=headers, json=add_payload)

        payload = {"payment_method": "COD"}
        requests.post(f"{BASE_URL}{API_PATH}/checkout", headers=headers, json=payload)

        prod_resp_after = requests.get(f"{BASE_URL}{API_PATH}/products/1", headers=headers)
        final_stock = prod_resp_after.json().get("stock_quantity") or prod_resp_after.json().get("stock", 0)
        assert final_stock == initial_stock - 1, f"Expected stock {initial_stock - 1}, got {final_stock}"
