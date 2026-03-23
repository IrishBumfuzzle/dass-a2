import pytest
import requests
from conftest import BASE_URL, API_PATH, get_headers


class TestAddresses:

    def test_get_addresses(self):
        headers = get_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/addresses", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_add_address_valid(self):
        headers = get_headers()
        payload = {
            "label": "HOME",
            "street": "123 Main Street",
            "city": "New York",
            "pincode": "100001",
            "is_default": False
        }
        response = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                headers=headers, json=payload)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"

    def test_add_address_returns_full_object(self):
        headers = get_headers()
        payload = {
            "label": "HOME",
            "street": "789 Full Object Street",
            "city": "Chicago",
            "pincode": "600001",
            "is_default": False
        }
        response = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                headers=headers, json=payload)
        assert response.status_code in [200, 201]
        data = response.json()
        addr = data.get("address", data)
        assert "address_id" in addr, "Response should contain address_id"
        assert "label" in addr, "Response should contain label"
        assert "street" in addr, "Response should contain street"
        assert "city" in addr, "Response should contain city"
        assert "pincode" in addr, "Response should contain pincode"
        assert "is_default" in addr, "Response should contain is_default"

    def test_add_address_invalid_label(self):
        headers = get_headers()
        payload = {
            "label": "INVALID",
            "street": "123 Main Street",
            "city": "New York",
            "pincode": "100001"
        }
        response = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_add_address_street_too_short(self):
        headers = get_headers()
        payload = {
            "label": "HOME",
            "street": "123",
            "city": "New York",
            "pincode": "100001"
        }
        response = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_add_address_street_too_long(self):
        headers = get_headers()
        payload = {
            "label": "HOME",
            "street": "A" * 101,
            "city": "New York",
            "pincode": "100001"
        }
        response = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_add_address_city_too_short(self):
        headers = get_headers()
        payload = {
            "label": "HOME",
            "street": "123 Main Street",
            "city": "A",
            "pincode": "100001"
        }
        response = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_add_address_city_too_long(self):
        headers = get_headers()
        payload = {
            "label": "HOME",
            "street": "123 Main Street",
            "city": "A" * 51,
            "pincode": "100001"
        }
        response = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_add_address_pincode_5_digits(self):
        headers = get_headers()
        payload = {
            "label": "HOME",
            "street": "Pincode 5 digits",
            "city": "New York",
            "pincode": "10000"
        }
        response = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_add_address_pincode_7_digits(self):
        headers = get_headers()
        payload = {
            "label": "HOME",
            "street": "Pincode 7 digits",
            "city": "New York",
            "pincode": "1000011"
        }
        response = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_add_address_non_numeric_pincode(self):
        headers = get_headers()
        payload = {
            "label": "HOME",
            "street": "Non numeric pincode",
            "city": "New York",
            "pincode": "10000a"
        }
        response = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_delete_non_existent_address(self):
        headers = get_headers()
        response = requests.delete(f"{BASE_URL}{API_PATH}/addresses/99999",
                                  headers=headers)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    def test_add_address_as_default(self):
        headers = get_headers()
        payload = {
            "label": "HOME",
            "street": "add default address street",
            "city": "New York",
            "pincode": "100001",
            "is_default": True
        }
        response = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                headers=headers, json=payload)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"

    def test_update_address_street_only(self):
        headers = get_headers()
        create_payload = {
            "label": "HOME",
            "street": "update street address only",
            "city": "New York",
            "pincode": "100001",
            "is_default": False
        }
        create_response = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                       headers=headers, json=create_payload)
        if create_response.status_code in [200, 201]:
            data = create_response.json()
            addr_id = data.get("address_id") or (data.get("address", {}).get("address_id") if "address" in data else None)
            if addr_id:
                update_payload = {"street": "456 Updated Street"}
                update_response = requests.put(f"{BASE_URL}{API_PATH}/addresses/{addr_id}",
                                              headers=headers, json=update_payload)
                assert update_response.status_code == 200, f"Expected 200, got {update_response.status_code}"

    def test_update_address_returns_new_data(self):
        headers = get_headers()
        create_payload = {
            "label": "OFFICE",
            "street": "Old Street Name For Update",
            "city": "Some City",
            "pincode": "654321",
            "is_default": False
        }
        post_res = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                headers=headers, json=create_payload)
        if post_res.status_code in [200, 201]:
            data = post_res.json()
            addr_id = data.get("address_id") or (data.get("address", {}).get("address_id") if "address" in data else None)
            if addr_id:
                update_payload = {"street": "Brand New Street Name"}
                put_res = requests.put(f"{BASE_URL}{API_PATH}/addresses/{addr_id}",
                                      headers=headers, json=update_payload)
                assert put_res.status_code == 200
                updated_data = put_res.json()
                addr = updated_data.get("address", updated_data)
                assert addr["street"] == "Brand New Street Name", \
                    f"Expected 'Brand New Street Name', got '{addr['street']}'"

    def test_update_address_as_default(self):
        headers = get_headers()
        create_payload = {
            "label": "HOME",
            "street": "update default address street",
            "city": "New York",
            "pincode": "100001",
            "is_default": False
        }
        create_response = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                       headers=headers, json=create_payload)
        if create_response.status_code in [200, 201]:
            data = create_response.json()
            addr_id = data.get("address_id") or (data.get("address", {}).get("address_id") if "address" in data else None)
            if addr_id:
                update_payload = {"is_default": True}
                update_response = requests.put(f"{BASE_URL}{API_PATH}/addresses/{addr_id}",
                                              headers=headers, json=update_payload)
                assert update_response.status_code == 200, f"Expected 200, got {update_response.status_code}"

    def test_update_non_existent_address(self):
        headers = get_headers()
        payload = {"street": "New Street"}
        response = requests.put(f"{BASE_URL}{API_PATH}/addresses/99999",
                               headers=headers, json=payload)
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    def test_delete_existing_address(self):
        headers = get_headers()
        create_payload = {
            "label": "OFFICE",
            "street": "789 Business Ave",
            "city": "Boston",
            "pincode": "200001",
            "is_default": False
        }
        create_response = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                       headers=headers, json=create_payload)
        if create_response.status_code in [200, 201]:
            data = create_response.json()
            addr_id = data.get("address_id") or (data.get("address", {}).get("address_id") if "address" in data else None)
            if addr_id:
                delete_response = requests.delete(f"{BASE_URL}{API_PATH}/addresses/{addr_id}",
                                                 headers=headers)
                assert delete_response.status_code in [200, 204], f"Expected 200/204, got {delete_response.status_code}"

                delete_again = requests.delete(f"{BASE_URL}{API_PATH}/addresses/{addr_id}",
                                              headers=headers)
                assert delete_again.status_code == 404, f"Expected 404, got {delete_again.status_code}"

    def test_update_immutable_field_label(self):
        headers = get_headers()
        create_payload = {
            "label": "HOME",
            "street": "123 Original Street",
            "city": "Boston",
            "pincode": "300001",
            "is_default": False
        }
        create_response = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                       headers=headers, json=create_payload)
        if create_response.status_code in [200, 201]:
            data = create_response.json()
            addr_id = data.get("address_id") or (data.get("address", {}).get("address_id") if "address" in data else None)
            if addr_id:
                update_payload = {"label": "OFFICE"}
                update_response = requests.put(f"{BASE_URL}{API_PATH}/addresses/{addr_id}",
                                              headers=headers, json=update_payload)
                if update_response.status_code in [200, 201]:
                    updated_data = update_response.json()
                    addr = updated_data.get("address", updated_data)
                    updated_label = addr.get("label")
                    assert updated_label == "HOME", f"Label should not change from HOME to {updated_label}"
                else:
                    assert update_response.status_code == 400, f"Expected 400 or 200 with unchanged label, got {update_response.status_code}"

    def test_update_default_when_another_is_default(self):
        headers = get_headers()

        create_payload1 = {
            "label": "HOME",
            "street": "321 First Default Addr",
            "city": "New York",
            "pincode": "100001",
            "is_default": True
        }
        create_response1 = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                        headers=headers, json=create_payload1)
        if create_response1.status_code in [200, 201]:
            create_payload2 = {
                "label": "OFFICE",
                "street": "654 Second Non Default Addr",
                "city": "Boston",
                "pincode": "200001",
                "is_default": False
            }
            create_response2 = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                            headers=headers, json=create_payload2)
            if create_response2.status_code in [200, 201]:
                data2 = create_response2.json()
                addr_id2 = data2.get("address_id") or (data2.get("address", {}).get("address_id") if "address" in data2 else None)
                if addr_id2:
                    update_payload = {"is_default": True}
                    update_response = requests.put(f"{BASE_URL}{API_PATH}/addresses/{addr_id2}",
                                                  headers=headers, json=update_payload)
                    assert update_response.status_code in [200, 201]

                    get_response = requests.get(f"{BASE_URL}{API_PATH}/addresses", headers=headers)
                    if get_response.status_code == 200:
                        addresses = get_response.json()
                        if isinstance(addresses, list):
                            default_count = sum(1 for a in addresses if a.get("is_default") is True)
                            assert default_count <= 1, f"Expected at most 1 default address, found {default_count}"

    def test_update_street_too_short(self):
        headers = get_headers()
        create_payload = {
            "label": "HOME",
            "street": "123 Valid Street Address",
            "city": "New York",
            "pincode": "100001",
            "is_default": False
        }
        create_response = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                       headers=headers, json=create_payload)
        if create_response.status_code in [200, 201]:
            data = create_response.json()
            addr_id = data.get("address_id") or (data.get("address", {}).get("address_id") if "address" in data else None)
            if addr_id:
                update_payload = {"street": "123"}  # Too short
                update_response = requests.put(f"{BASE_URL}{API_PATH}/addresses/{addr_id}",
                                              headers=headers, json=update_payload)
                assert update_response.status_code == 400, f"Expected 400 for street too short, got {update_response.status_code}"

    def test_update_street_too_long(self):
        headers = get_headers()
        create_payload = {
            "label": "HOME",
            "street": "123 Valid Street Address",
            "city": "New York",
            "pincode": "100001",
            "is_default": False
        }
        create_response = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                       headers=headers, json=create_payload)
        if create_response.status_code in [200, 201]:
            data = create_response.json()
            addr_id = data.get("address_id") or (data.get("address", {}).get("address_id") if "address" in data else None)
            if addr_id:
                update_payload = {"street": "A" * 101}  # Too long
                update_response = requests.put(f"{BASE_URL}{API_PATH}/addresses/{addr_id}",
                                              headers=headers, json=update_payload)
                assert update_response.status_code == 400, f"Expected 400 for street too long, got {update_response.status_code}"

    def test_add_address_valid_labels(self):
        headers = get_headers()
        for label in ["HOME", "OFFICE", "OTHER"]:
            payload = {
                "label": label,
                "street": f"Street for {label}",
                "city": "Test City",
                "pincode": "100001",
                "is_default": False
            }
            response = requests.post(f"{BASE_URL}{API_PATH}/addresses",
                                    headers=headers, json=payload)
            assert response.status_code in [200, 201], f"Expected 200/201 for label {label}, got {response.status_code}"
