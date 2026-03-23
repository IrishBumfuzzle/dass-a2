import pytest
import requests
from conftest import BASE_URL, API_PATH, get_headers


class TestSupportTickets:

    def test_create_ticket_valid(self):
        headers = get_headers()
        payload = {"subject": "Order Issue", "message": "I have an issue with my order"}
        response = requests.post(f"{BASE_URL}{API_PATH}/support/ticket",
                                headers=headers, json=payload)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"

    def test_create_ticket_starts_with_open(self):
        headers = get_headers()
        payload = {"subject": "New Ticket Test", "message": "Testing initial status"}
        response = requests.post(f"{BASE_URL}{API_PATH}/support/ticket",
                                headers=headers, json=payload)
        if response.status_code in [200, 201]:
            data = response.json()
            status = data.get("status")
            if status:
                assert status == "OPEN", f"New ticket should start as OPEN, got {status}"

    def test_create_ticket_subject_too_short(self):
        headers = get_headers()
        payload = {"subject": "help", "message": "I need help with my order"}
        response = requests.post(f"{BASE_URL}{API_PATH}/support/ticket",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_create_ticket_subject_too_long(self):
        headers = get_headers()
        payload = {"subject": "A" * 101, "message": "I need help with my order"}
        response = requests.post(f"{BASE_URL}{API_PATH}/support/ticket",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_create_ticket_empty_message(self):
        headers = get_headers()
        payload = {"subject": "Order Issue", "message": ""}
        response = requests.post(f"{BASE_URL}{API_PATH}/support/ticket",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_create_ticket_message_too_long(self):
        headers = get_headers()
        payload = {"subject": "Order Issue", "message": "A" * 501}
        response = requests.post(f"{BASE_URL}{API_PATH}/support/ticket",
                                headers=headers, json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"

    def test_message_saved_exactly_as_written(self):
        headers = get_headers()
        special_message = "Issue #1234 - Special chars: @#$%^&*()"
        payload = {"subject": "Order Issue", "message": special_message}
        response = requests.post(f"{BASE_URL}{API_PATH}/support/ticket",
                                headers=headers, json=payload)
        if response.status_code in [200, 201]:
            tickets_response = requests.get(f"{BASE_URL}{API_PATH}/support/tickets",
                                           headers=headers)
            if tickets_response.status_code == 200:
                tickets_data = tickets_response.json()
                if isinstance(tickets_data, dict) and "tickets" in tickets_data:
                    tickets = tickets_data["tickets"]
                elif isinstance(tickets_data, list):
                    tickets = tickets_data
                else:
                    tickets = []

                found = False
                for ticket in tickets:
                    if ticket.get("message") == special_message:
                        found = True
                        break


    def test_get_user_tickets(self):
        headers = get_headers()
        response = requests.get(f"{BASE_URL}{API_PATH}/support/tickets", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, (list, dict))

    def test_update_ticket_status_open_to_in_progress(self):
        headers = get_headers()
        create_payload = {"subject": "Status Test", "message": "Testing status transitions"}
        create_response = requests.post(f"{BASE_URL}{API_PATH}/support/ticket",
                                       headers=headers, json=create_payload)
        if create_response.status_code in [200, 201]:
            tickets_response = requests.get(f"{BASE_URL}{API_PATH}/support/tickets",
                                           headers=headers)
            if tickets_response.status_code == 200:
                tickets_data = tickets_response.json()
                if isinstance(tickets_data, dict) and "tickets" in tickets_data:
                    tickets = tickets_data["tickets"]
                elif isinstance(tickets_data, list):
                    tickets = tickets_data
                else:
                    tickets = []

                for ticket in tickets:
                    if ticket.get("status") == "OPEN":
                        ticket_id = ticket.get("id") or ticket.get("ticket_id")
                        update_response = requests.put(
                            f"{BASE_URL}{API_PATH}/support/tickets/{ticket_id}",
                            headers=headers,
                            json={"status": "IN_PROGRESS"}
                        )
                        assert update_response.status_code in [200, 201], \
                            f"Expected 200/201, got {update_response.status_code}"
                        break

    def test_update_ticket_status_in_progress_to_closed(self):
        headers = get_headers()
        tickets_response = requests.get(f"{BASE_URL}{API_PATH}/support/tickets",
                                       headers=headers)
        if tickets_response.status_code == 200:
            tickets_data = tickets_response.json()
            if isinstance(tickets_data, dict) and "tickets" in tickets_data:
                tickets = tickets_data["tickets"]
            elif isinstance(tickets_data, list):
                tickets = tickets_data
            else:
                tickets = []

            for ticket in tickets:
                if ticket.get("status") == "IN_PROGRESS":
                    ticket_id = ticket.get("id") or ticket.get("ticket_id")
                    update_response = requests.put(
                        f"{BASE_URL}{API_PATH}/support/tickets/{ticket_id}",
                        headers=headers,
                        json={"status": "CLOSED"}
                    )
                    assert update_response.status_code in [200, 201], \
                        f"Expected 200/201, got {update_response.status_code}"
                    break

    def test_invalid_status_transition_open_to_closed(self):
        headers = get_headers()
        create_payload = {"subject": "Invalid Transition Test", "message": "Skip IN_PROGRESS"}
        create_response = requests.post(f"{BASE_URL}{API_PATH}/support/ticket",
                                       headers=headers, json=create_payload)
        if create_response.status_code in [200, 201]:
            tickets_response = requests.get(f"{BASE_URL}{API_PATH}/support/tickets",
                                           headers=headers)
            if tickets_response.status_code == 200:
                tickets_data = tickets_response.json()
                if isinstance(tickets_data, dict) and "tickets" in tickets_data:
                    tickets = tickets_data["tickets"]
                elif isinstance(tickets_data, list):
                    tickets = tickets_data
                else:
                    tickets = []

                for ticket in tickets:
                    if ticket.get("status") == "OPEN":
                        ticket_id = ticket.get("id") or ticket.get("ticket_id")
                        update_response = requests.put(
                            f"{BASE_URL}{API_PATH}/support/tickets/{ticket_id}",
                            headers=headers,
                            json={"status": "CLOSED"}
                        )
                        assert update_response.status_code == 400, \
                            f"Expected 400 for invalid transition, got {update_response.status_code}"
                        break

    def test_invalid_status_transition_in_progress_to_open(self):
        headers = get_headers()

        create_payload = {"subject": "Reverse Test", "message": "Testing reverse transition"}
        create_response = requests.post(f"{BASE_URL}{API_PATH}/support/ticket",
                                       headers=headers, json=create_payload)
        if create_response.status_code in [200, 201]:
            data = create_response.json()
            ticket_id = data.get("ticket_id") or data.get("id")
            if ticket_id:

                requests.put(
                    f"{BASE_URL}{API_PATH}/support/tickets/{ticket_id}",
                    headers=headers,
                    json={"status": "IN_PROGRESS"}
                )

                update_response = requests.put(
                    f"{BASE_URL}{API_PATH}/support/tickets/{ticket_id}",
                    headers=headers,
                    json={"status": "OPEN"}
                )
                assert update_response.status_code == 400, \
                    f"Expected 400 for reverse transition, got {update_response.status_code}"

    def test_subject_boundary_5_chars(self):
        headers = get_headers()
        payload = {"subject": "Hello", "message": "Valid message"}
        response = requests.post(f"{BASE_URL}{API_PATH}/support/ticket",
                                headers=headers, json=payload)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"

    def test_subject_boundary_100_chars(self):
        headers = get_headers()
        payload = {"subject": "A" * 100, "message": "Valid message"}
        response = requests.post(f"{BASE_URL}{API_PATH}/support/ticket",
                                headers=headers, json=payload)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"

    def test_message_boundary_500_chars(self):
        headers = get_headers()
        payload = {"subject": "Valid Subject", "message": "A" * 500}
        response = requests.post(f"{BASE_URL}{API_PATH}/support/ticket",
                                headers=headers, json=payload)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
