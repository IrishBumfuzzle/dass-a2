import pytest
import requests
from conftest import BASE_URL, API_PATH, get_headers


class TestProducts:

    def test_get_all_products(self):
        headers = get_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/products", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_get_product_by_id(self):
        headers = get_headers()
        list_response = requests.get(f"{BASE_URL}{API_PATH}/products", headers=headers)
        if list_response.status_code == 200:
            products = list_response.json()
            product_id = products[0].get("product_id")
            response = requests.get(f"{BASE_URL}{API_PATH}/products/{product_id}",
                                    headers=headers)
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    def test_get_non_existent_product(self):
        headers = get_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/products/99999", headers=headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    def test_get_products_with_search(self):
        headers = get_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/products?search=test",
                               headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data == [], f"Expected empty list, got {data}"

    def test_get_products_sort_price_asc(self):
        headers = get_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/products?sort=price_asc",
                               headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        price = [p.get("price") for p in data]
        assert price == sorted(price), f"Expected sorted prices, got {price}"
        

    def test_get_products_sort_price_desc(self):
        headers = get_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/products?sort=price_desc",
                               headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        price = [p.get("price") for p in data]
        assert price == sorted(price, reverse=True), f"Expected sorted prices, got {price}"

    def test_get_products_filter_by_category(self):
        headers = get_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/products?category=Electronics",
                               headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        for p in data:
            assert p.get("category") == "Electronics", f"Expected category Electronics, got {p.get('category')}"

    def test_verify_exact_product_price(self):
        headers = get_headers()
        list_response = requests.get(f"{BASE_URL}{API_PATH}/products", headers=headers)
        if list_response.status_code == 200:
            products = list_response.json()
            product_price = products[0].get("price")
            product_id = products[0].get("id") or products[0].get("product_id")

            response = requests.get(f"{BASE_URL}{API_PATH}/products/{product_id}",
                                    headers=headers)
            if response.status_code == 200:
                product_data = response.json()
                assert product_data.get("price") == product_price, \
                    f"Price mismatch: {product_data.get('price')} != {product_price}"

    def test_nonexistent_product_price(self):
        headers = get_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/products/99999", headers=headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    def test_product_list_shows_only_active_products(self):
        headers = get_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/products", headers=headers)
        assert response.status_code == 200

        data = response.json()
        products = data

        for product in products:
            status = product.get("is_active")
            assert status is True, f"Product {product.get('product_id')} is inactive but returned in list"

    def test_price_matches_admin_database(self):
        headers = get_headers()
        from conftest import get_admin_headers
        admin_headers = get_admin_headers()

        admin_prods = requests.get(f"{BASE_URL}{API_PATH}/admin/products", headers=admin_headers)
        user_prods = requests.get(f"{BASE_URL}{API_PATH}/products", headers=headers)

        if admin_prods.status_code == 200 and user_prods.status_code == 200:
            admin_data = admin_prods.json()
            user_data = user_prods.json()

            if isinstance(admin_data, list) and isinstance(user_data, list):
                admin_prices = {p.get("product_id"): p.get("price") for p in admin_data}
                for p in user_data:
                    pid = p.get("product_id")
                    if pid in admin_prices:
                        assert p.get("price") == admin_prices[pid], \
                            f"Price mismatch for product {pid}: user API shows {p.get('price')}, admin shows {admin_prices[pid]}"
