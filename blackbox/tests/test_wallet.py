import pytest
import requests
from conftest import BASE_URL, API_PATH, get_headers


class TestWallet:

    def test_get_wallet(self):
        headers = get_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/wallet", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "balance" in data or "amount" in data or "wallet_balance" in data

    def test_add_wallet_amount_valid(self):
        headers = get_headers()
        payload = {"amount": 1000}
        response = requests.post(f"{BASE_URL}{API_PATH}/wallet/add",
                                headers=headers, json=payload)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"

    def test_add_wallet_amount_zero(self):
        headers = get_headers()
        payload = {"amount": 0}
        response = requests.post(f"{BASE_URL}{API_PATH}/wallet/add",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_add_wallet_negative_amount(self):
        headers = get_headers()
        payload = {"amount": -100}
        response = requests.post(f"{BASE_URL}{API_PATH}/wallet/add",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_add_wallet_exceeding_maximum(self):
        headers = get_headers()
        payload = {"amount": 100001}
        response = requests.post(f"{BASE_URL}{API_PATH}/wallet/add",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_add_wallet_boundary_maximum(self):
        headers = get_headers()
        payload = {"amount": 100000}
        response = requests.post(f"{BASE_URL}{API_PATH}/wallet/add",
                                headers=headers, json=payload)
        assert response.status_code in [200, 201], f"Expected 200/201 for exactly 100000, got {response.status_code}"

    def test_add_wallet_balance_increases(self):
        headers = get_headers()
        bal_before = requests.get(f"{BASE_URL}{API_PATH}/wallet", headers=headers).json()
        before = bal_before.get("balance") or bal_before.get("wallet_balance") or bal_before.get("amount") or 0

        payload = {"amount": 500}
        requests.post(f"{BASE_URL}{API_PATH}/wallet/add", headers=headers, json=payload)

        bal_after = requests.get(f"{BASE_URL}{API_PATH}/wallet", headers=headers).json()
        after = bal_after.get("balance") or bal_after.get("wallet_balance") or bal_after.get("amount") or 0
        assert abs(after - (before + 500)) < 0.01, \
            f"Expected balance {before + 500}, got {after}"

    def test_pay_from_wallet_valid(self):
        headers = get_headers()
        add_payload = {"amount": 5000}
        requests.post(f"{BASE_URL}{API_PATH}/wallet/add", headers=headers, json=add_payload)

        pay_payload = {"amount": 500}
        response = requests.post(f"{BASE_URL}{API_PATH}/wallet/pay",
                                headers=headers, json=pay_payload)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"

    def test_pay_from_wallet_zero_amount(self):
        headers = get_headers()
        payload = {"amount": 0}
        response = requests.post(f"{BASE_URL}{API_PATH}/wallet/pay",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_pay_from_wallet_more_than_balance(self):
        headers = get_headers()
        balance_response = requests.get(f"{BASE_URL}{API_PATH}/wallet", headers=headers)
        if balance_response.status_code == 200:
            balance_data = balance_response.json()
            current_balance = balance_data.get("balance") or balance_data.get("wallet_balance") or balance_data.get("amount") or 0

            pay_payload = {"amount": current_balance + 10000}
            response = requests.post(f"{BASE_URL}{API_PATH}/wallet/pay",
                                    headers=headers, json=pay_payload)
            assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_pay_exact_amount_deducted(self):
        headers = get_headers()
        requests.post(f"{BASE_URL}{API_PATH}/wallet/add", headers=headers, json={"amount": 1000})

        bal_before = requests.get(f"{BASE_URL}{API_PATH}/wallet", headers=headers).json()
        before = bal_before.get("balance") or bal_before.get("wallet_balance") or bal_before.get("amount") or 0

        pay_amount = 100
        requests.post(f"{BASE_URL}{API_PATH}/wallet/pay", headers=headers, json={"amount": pay_amount})

        bal_after = requests.get(f"{BASE_URL}{API_PATH}/wallet", headers=headers).json()
        after = bal_after.get("balance") or bal_after.get("wallet_balance") or bal_after.get("amount") or 0

        assert abs(after - (before - pay_amount)) < 0.01, \
            f"Expected balance {before - pay_amount}, got {after}. Extra amount was deducted!"

    def test_pay_from_wallet_exact_balance(self):
        headers = get_headers()
        balance_response = requests.get(f"{BASE_URL}{API_PATH}/wallet", headers=headers)
        if balance_response.status_code == 200:
            balance_data = balance_response.json()
            current_balance = balance_data.get("balance") or balance_data.get("wallet_balance") or balance_data.get("amount") or 0
            if current_balance > 0:
                pay_payload = {"amount": current_balance}
                response = requests.post(f"{BASE_URL}{API_PATH}/wallet/pay",
                                        headers=headers, json=pay_payload)
                assert response.status_code in [200, 201, 400], f"Got {response.status_code}"
