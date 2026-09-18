"""Tests for the employee onboarding application."""

import http.client
import re
import sqlite3
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.parse import urlencode

from onboarding_app import (
    DEPARTMENTS,
    OFFICE_LOCATIONS,
    OnboardingHandler,
    create_onboarding_record,
    create_draft,
    get_draft,
    get_request,
    init_db,
    list_requests,
    normalize_form,
    update_status,
    validate_request,
)


def valid_request_data():
    return {
        "employee_id": "",
        "first_name": "Asha",
        "last_name": "Rao",
        "personal_email": "asha@example.com",
        "official_email": "asha.rao@example.com",
        "mobile_number": "+919900000000",
        "joining_date": "2026-10-01",
        "employee_type": "Full Time",
        "department": "IT",
        "job_title": "Analyst",
        "cost_center": "CC-101",
        "manager_name": "Hiring Manager",
        "manager_email": "manager@example.com",
        "skip_manager": "",
        "country": "India",
        "office_location": "Mumbai",
        "work_mode": "Hybrid",
        "laptop_required": "Yes",
        "mobile_device_required": "No",
        "vpn_required": "Yes",
        "special_application_access": "Finance dashboard",
        "special_accommodation_requirements": "",
        "security_clearance_requirements": "Standard background check",
        "other_comments": "",
    }


class TestOnboardingApp(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        init_db(self.connection)

    def tearDown(self):
        self.connection.close()

    def test_init_db_loads_lookup_tables(self):
        departments = [
            row["Department"]
            for row in self.connection.execute("SELECT Department FROM Departments")
        ]
        locations = [
            row["Location"]
            for row in self.connection.execute("SELECT Location FROM OfficeLocations")
        ]

        self.assertEqual(departments, list(DEPARTMENTS))
        self.assertEqual(locations, list(OFFICE_LOCATIONS))

    def test_create_onboarding_record_stores_main_table_columns(self):
        request_id = create_onboarding_record(self.connection, valid_request_data())

        record = get_request(self.connection, request_id)

        self.assertIsNotNone(record)
        self.assertEqual(record["EmployeeName"], "Asha Rao")
        self.assertEqual(record["JoinDate"], "2026-10-01")
        self.assertEqual(record["Manager"], "Hiring Manager")
        self.assertEqual(record["Department"], "IT")
        self.assertEqual(record["Location"], "India - Mumbai")
        self.assertEqual(record["LaptopRequired"], "Yes")
        self.assertEqual(record["VPNRequired"], "Yes")
        self.assertEqual(record["Status"], "Submitted")

    def test_validate_request_requires_required_fields(self):
        data = valid_request_data()
        data["first_name"] = ""

        self.assertIn("First Name", validate_request(data))

    def test_validate_request_rejects_invalid_lookup_values(self):
        data = valid_request_data()
        data["department"] = "Legal"

        self.assertIn("Department must be a configured option", validate_request(data))

    def test_validate_request_rejects_invalid_contact_fields(self):
        data = valid_request_data()
        data["personal_email"] = "not-an-email"
        data["mobile_number"] = "abc"

        errors = validate_request(data)

        self.assertIn("Personal Email must be a valid email", errors)
        self.assertIn("Mobile Number must be a valid phone number", errors)

    def test_status_flow_manager_approval_then_hr_ready(self):
        request_id = create_onboarding_record(self.connection, valid_request_data())
        record = get_request(self.connection, request_id)

        self.assertTrue(
            update_status(
                self.connection,
                request_id,
                "Manager Approved",
                record["ManagerActionToken"],
            )
        )
        self.assertEqual(get_request(self.connection, request_id)["Status"], "Manager Approved")
        record = get_request(self.connection, request_id)
        self.assertTrue(
            update_status(
                self.connection,
                request_id,
                "Onboarding Ready",
                record["HrActionToken"],
            )
        )
        self.assertEqual(get_request(self.connection, request_id)["Status"], "Onboarding Ready")

    def test_status_flow_allows_manager_rejection(self):
        request_id = create_onboarding_record(self.connection, valid_request_data())
        record = get_request(self.connection, request_id)

        self.assertTrue(
            update_status(
                self.connection,
                request_id,
                "Rejected",
                record["ManagerActionToken"],
            )
        )

        self.assertEqual(get_request(self.connection, request_id)["Status"], "Rejected")

    def test_status_flow_rejects_invalid_transition(self):
        request_id = create_onboarding_record(self.connection, valid_request_data())
        record = get_request(self.connection, request_id)

        with self.assertRaises(ValueError):
            update_status(
                self.connection,
                request_id,
                "Onboarding Ready",
                record["HrActionToken"],
            )

    def test_status_flow_rejects_missing_action_token(self):
        request_id = create_onboarding_record(self.connection, valid_request_data())

        with self.assertRaises(PermissionError):
            update_status(self.connection, request_id, "Manager Approved")

    def test_create_and_get_draft_stores_reviewed_data(self):
        data = valid_request_data()
        token = create_draft(self.connection, data)

        draft = get_draft(self.connection, token)

        self.assertEqual(draft["first_name"], "Asha")
        self.assertEqual(draft["department"], "IT")

    def test_list_requests_returns_newest_requests(self):
        first_request = create_onboarding_record(self.connection, valid_request_data())
        second_data = valid_request_data()
        second_data["first_name"] = "Dev"
        second_request = create_onboarding_record(self.connection, second_data)

        request_ids = [row["RequestId"] for row in list_requests(self.connection)]

        self.assertIn(first_request, request_ids)
        self.assertIn(second_request, request_ids)

    def test_normalize_form_includes_missing_fields_as_empty_strings(self):
        normalized = normalize_form({"first_name": [" Asha "]})

        self.assertEqual(normalized["first_name"], "Asha")
        self.assertEqual(normalized["last_name"], "")


class TestOnboardingHttpFlow(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = f"{self.temp_dir.name}/onboarding-test.db"

        class TestHandler(OnboardingHandler):
            def log_message(self, format, *args):
                return

        TestHandler.db_path = self.db_path
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), TestHandler)
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()
        self.host, self.port = self.server.server_address

    def tearDown(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()
        self.temp_dir.cleanup()

    def request(self, method, path, body=None):
        connection = http.client.HTTPConnection(self.host, self.port)
        headers = {}
        if body is not None:
            body = urlencode(body)
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        content = response.read().decode()
        connection.close()
        return response.status, content

    def test_http_review_submit_approval_and_hr_flow(self):
        status, submit_body = self.submit_valid_request()
        request_id = re.search(
            r"<tr><th>Request ID</th><td>([^<]+)</td></tr>", submit_body
        ).group(1)
        manager_code = self.get_request_token(request_id, "ManagerActionToken")

        self.assertEqual(status, 200)
        self.assertIn("Submitted", submit_body)

        status, manager_body = self.request(
            "POST",
            f"/manager/{request_id}",
            {"token": manager_code, "decision": "approve"},
        )
        hr_code = self.get_request_token(request_id, "HrActionToken")

        self.assertEqual(status, 200)
        self.assertIn("Manager Approved", manager_body)

        status, hr_body = self.request(
            "POST", f"/hr/{request_id}", {"token": hr_code}
        )

        self.assertEqual(status, 200)
        self.assertIn("Onboarding Ready", hr_body)

    def test_http_manager_action_requires_valid_code(self):
        status, submit_body = self.submit_valid_request()
        request_id = re.search(
            r"<tr><th>Request ID</th><td>([^<]+)</td></tr>", submit_body
        ).group(1)

        status, manager_body = self.request(
            "POST",
            f"/manager/{request_id}",
            {"token": "wrong-token", "decision": "approve"},
        )

        self.assertEqual(status, 400)
        self.assertIn("Invalid or missing action token", manager_body)

    def test_http_hr_action_requires_valid_code(self):
        status, submit_body = self.submit_valid_request()
        request_id = re.search(
            r"<tr><th>Request ID</th><td>([^<]+)</td></tr>", submit_body
        ).group(1)
        manager_code = self.get_request_token(request_id, "ManagerActionToken")
        self.request(
            "POST",
            f"/manager/{request_id}",
            {"token": manager_code, "decision": "approve"},
        )

        status, hr_body = self.request(
            "POST", f"/hr/{request_id}", {"token": "wrong-token"}
        )

        self.assertEqual(status, 400)
        self.assertIn("Invalid or missing action token", hr_body)

    def test_http_manager_action_rejects_invalid_decision(self):
        status, submit_body = self.submit_valid_request()
        request_id = re.search(
            r"<tr><th>Request ID</th><td>([^<]+)</td></tr>", submit_body
        ).group(1)
        manager_code = self.get_request_token(request_id, "ManagerActionToken")

        status, manager_body = self.request(
            "POST",
            f"/manager/{request_id}",
            {"token": manager_code, "decision": "maybe"},
        )

        self.assertEqual(status, 400)
        self.assertIn("Invalid manager decision", manager_body)

    def submit_valid_request(self):
        status, review_body = self.request("POST", "/review", valid_request_data())
        draft_token = re.search(r'name="token" value="([^"]+)"', review_body).group(1)

        self.assertEqual(status, 200)
        self.assertIn("Review &amp; Submit", review_body)

        status, submit_body = self.request("POST", "/submit", {"token": draft_token})

        self.assertEqual(status, 200)
        self.assertIn("Submitted", submit_body)
        return status, submit_body

    def get_request_token(self, request_id, column):
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            return connection.execute(
                f"SELECT {column} FROM EmployeeOnboarding WHERE RequestId = ?",
                (request_id,),
            ).fetchone()[column]


if __name__ == "__main__":
    unittest.main()
