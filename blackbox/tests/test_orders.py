import pytest
import requests
from conftest import BASE_URL, API_PATH, get_headers


class TestOrders:

    def test_get_all_orders(self):
        headers = get_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/orders", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_get_specific_order(self):
        headers = get_headers()
        list_response = requests.get(f"{BASE_URL}{API_PATH}/orders", headers=headers)
        if list_response.status_code == 200:
            orders = list_response.json()
            if isinstance(orders, dict) and "orders" in orders:
                orders = orders["orders"]
            if isinstance(orders, list) and len(orders) > 0:
                order_id = orders[0].get("id") or orders[0].get("order_id")
                response = requests.get(f"{BASE_URL}{API_PATH}/orders/{order_id}",
                                       headers=headers)
                assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_get_non_existent_order(self):
        headers = get_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/orders/99999", headers=headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    def test_cancel_non_existent_order(self):
        headers = get_headers()
        response = requests.post(f"{BASE_URL}{API_PATH}/orders/99999/cancel",
                                headers=headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    def test_cancel_delivered_order(self):
        headers = get_headers()
        list_response = requests.get(f"{BASE_URL}{API_PATH}/orders", headers=headers)
        if list_response.status_code == 200:
            orders = list_response.json()
            if isinstance(orders, dict) and "orders" in orders:
                orders = orders["orders"]
            if isinstance(orders, list):
                for order in orders:
                    if order.get("status") == "DELIVERED" or order.get("order_status") == "DELIVERED":
                        order_id = order.get("id") or order.get("order_id")
                        response = requests.post(f"{BASE_URL}{API_PATH}/orders/{order_id}/cancel",
                                               headers=headers)
                        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
                        break

    def test_cancel_order_restores_stock(self):
        headers = get_headers()

        requests.delete(f"{BASE_URL}{API_PATH}/cart/clear", headers=headers)
        add_payload = {"product_id": 1, "quantity": 1}
        requests.post(f"{BASE_URL}{API_PATH}/cart/add", headers=headers, json=add_payload)

        prod_before = requests.get(f"{BASE_URL}{API_PATH}/products/1", headers=headers)
        stock_before = prod_before.json().get("stock_quantity") or prod_before.json().get("stock", 0)

        checkout_resp = requests.post(f"{BASE_URL}{API_PATH}/checkout",
                                     headers=headers, json={"payment_method": "COD"})
        if checkout_resp.status_code in [200, 201]:
            order_id = checkout_resp.json().get("order_id") or checkout_resp.json().get("id")
            if order_id:

                prod_after_checkout = requests.get(f"{BASE_URL}{API_PATH}/products/1", headers=headers)
                stock_after_checkout = prod_after_checkout.json().get("stock_quantity") or prod_after_checkout.json().get("stock", 0)

                cancel_resp = requests.post(f"{BASE_URL}{API_PATH}/orders/{order_id}/cancel",
                                           headers=headers)
                if cancel_resp.status_code in [200, 201]:

                    prod_after_cancel = requests.get(f"{BASE_URL}{API_PATH}/products/1", headers=headers)
                    stock_after_cancel = prod_after_cancel.json().get("stock_quantity") or prod_after_cancel.json().get("stock", 0)
                    assert stock_after_cancel == stock_after_checkout + 1, \
                        f"Stock should be restored after cancel. Expected {stock_after_checkout + 1}, got {stock_after_cancel}"

    def test_get_order_invoice(self):
        headers = get_headers()
        list_response = requests.get(f"{BASE_URL}{API_PATH}/orders", headers=headers)
        if list_response.status_code == 200:
            orders = list_response.json()
            if isinstance(orders, dict) and "orders" in orders:
                orders = orders["orders"]
            if isinstance(orders, list) and len(orders) > 0:
                order_id = orders[0].get("id") or orders[0].get("order_id")
                response = requests.get(f"{BASE_URL}{API_PATH}/orders/{order_id}/invoice",
                                       headers=headers)
                assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_invoice_gst_calculation(self):
        headers = get_headers()
        list_response = requests.get(f"{BASE_URL}{API_PATH}/orders", headers=headers)
        if list_response.status_code == 200:
            orders = list_response.json()
            if isinstance(orders, dict) and "orders" in orders:
                orders = orders["orders"]
            if isinstance(orders, list) and len(orders) > 0:
                order_id = orders[0].get("id") or orders[0].get("order_id")
                invoice_response = requests.get(f"{BASE_URL}{API_PATH}/orders/{order_id}/invoice",
                                               headers=headers)
                if invoice_response.status_code == 200:
                    invoice_data = invoice_response.json()
                    subtotal = invoice_data.get("subtotal", 0)
                    gst = invoice_data.get("gst", 0) or invoice_data.get("gst_amount", 0)
                    expected_gst = subtotal * 0.05
                    assert abs(gst - expected_gst) < 0.01, f"GST {gst} != 5% of {subtotal}"

    def test_invoice_total_correctness(self):
        headers = get_headers()
        list_response = requests.get(f"{BASE_URL}{API_PATH}/orders", headers=headers)
        if list_response.status_code == 200:
            orders = list_response.json()
            if isinstance(orders, dict) and "orders" in orders:
                orders = orders["orders"]
            if isinstance(orders, list) and len(orders) > 0:
                order_id = orders[0].get("id") or orders[0].get("order_id")
                invoice_response = requests.get(f"{BASE_URL}{API_PATH}/orders/{order_id}/invoice",
                                               headers=headers)
                if invoice_response.status_code == 200:
                    invoice_data = invoice_response.json()
                    subtotal = invoice_data.get("subtotal", 0)
                    gst = invoice_data.get("gst", 0) or invoice_data.get("gst_amount", 0)
                    total = invoice_data.get("total", 0) or invoice_data.get("total_amount", 0)
                    expected_total = subtotal + gst
                    assert abs(total - expected_total) < 0.01, \
                        f"Total {total} != {subtotal} + {gst}"
