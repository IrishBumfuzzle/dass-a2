import pytest
import requests
from conftest import BASE_URL, API_PATH, get_headers


class TestReviews:

    def test_get_product_reviews(self):
        headers = get_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/products/1/reviews",
                               headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_add_review_valid(self):
        headers = get_headers()
        payload = {"rating": 4, "comment": "Great product, highly recommend!"}
        response = requests.post(f"{BASE_URL}{API_PATH}/products/1/reviews",
                                headers=headers, json=payload)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"

    def test_add_review_rating_too_low(self):
        headers = get_headers()
        payload = {"rating": 0, "comment": "Product review"}
        response = requests.post(f"{BASE_URL}{API_PATH}/products/1/reviews",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_add_review_rating_too_high(self):
        headers = get_headers()
        payload = {"rating": 6, "comment": "Product review"}
        response = requests.post(f"{BASE_URL}{API_PATH}/products/1/reviews",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_add_review_negative_rating(self):
        headers = get_headers()
        payload = {"rating": -1, "comment": "Bad product review"}
        response = requests.post(f"{BASE_URL}{API_PATH}/products/1/reviews",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_add_review_empty_comment(self):
        headers = get_headers()
        payload = {"rating": 4, "comment": ""}
        response = requests.post(f"{BASE_URL}{API_PATH}/products/1/reviews",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_add_review_comment_too_long(self):
        headers = get_headers()
        payload = {"rating": 4, "comment": "A" * 201}
        response = requests.post(f"{BASE_URL}{API_PATH}/products/1/reviews",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_verify_average_rating_is_decimal(self):
        headers = get_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/products/1/reviews",
                               headers=headers)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "average_rating" in data:
                avg_rating = data["average_rating"]
                assert isinstance(avg_rating, (int, float)), "Average rating should be numeric"

    def test_product_with_no_reviews_average_rating_zero(self):
        headers = get_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/products/9999/reviews",
                               headers=headers)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "average_rating" in data:
                avg_rating = data["average_rating"]
                assert avg_rating == 0, f"Product with no reviews should have average rating 0, got {avg_rating}"

    def test_review_rating_boundary_1(self):
        headers = get_headers()
        payload = {"rating": 1, "comment": "Minimum rating"}
        response = requests.post(f"{BASE_URL}{API_PATH}/products/1/reviews",
                                headers=headers, json=payload)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"

    def test_review_rating_boundary_5(self):
        headers = get_headers()
        payload = {"rating": 5, "comment": "Maximum rating"}
        response = requests.post(f"{BASE_URL}{API_PATH}/products/1/reviews",
                                headers=headers, json=payload)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"

    def test_review_comment_boundary_1_char(self):
        headers = get_headers()
        payload = {"rating": 3, "comment": "X"}
        response = requests.post(f"{BASE_URL}{API_PATH}/products/1/reviews",
                                headers=headers, json=payload)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"

    def test_review_comment_boundary_200_chars(self):
        headers = get_headers()
        payload = {"rating": 3, "comment": "A" * 200}
        response = requests.post(f"{BASE_URL}{API_PATH}/products/1/reviews",
                                headers=headers, json=payload)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
