"""Tests for the employee onboarding application."""

import sqlite3
import unittest

from onboarding_app import (
    DEPARTMENTS,
    OFFICE_LOCATIONS,
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


if __name__ == "__main__":
    unittest.main()
