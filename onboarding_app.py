"""Self-contained employee onboarding request web application."""

from __future__ import annotations

import html
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, urlparse


DB_PATH = Path(__file__).with_name("onboarding.db")
STATUSES = ("Submitted", "Manager Approved", "Rejected", "Onboarding Ready")
EMPLOYEE_TYPES = ("Full Time", "Contractor", "Intern", "Vendor")
WORK_MODES = ("Remote", "Hybrid", "Office")
DEPARTMENTS = ("Finance", "HR", "IT", "Sales")
OFFICE_LOCATIONS = ("Mumbai", "Pune", "Bangalore", "Hyderabad")

FORM_FIELDS = (
    "employee_id",
    "first_name",
    "last_name",
    "personal_email",
    "official_email",
    "mobile_number",
    "joining_date",
    "employee_type",
    "department",
    "job_title",
    "cost_center",
    "manager_name",
    "manager_email",
    "skip_manager",
    "country",
    "office_location",
    "work_mode",
    "laptop_required",
    "mobile_device_required",
    "vpn_required",
    "special_application_access",
    "special_accommodation_requirements",
    "security_clearance_requirements",
    "other_comments",
)

REQUIRED_FIELDS = (
    "first_name",
    "last_name",
    "personal_email",
    "mobile_number",
    "joining_date",
    "employee_type",
    "department",
    "job_title",
    "cost_center",
    "manager_name",
    "manager_email",
    "country",
    "office_location",
    "work_mode",
    "laptop_required",
    "mobile_device_required",
    "vpn_required",
)


def connect(db_path: str | Path = DB_PATH) -> sqlite3.Connection:
    """Return a SQLite connection configured for dictionary-like rows."""
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(connection: sqlite3.Connection) -> None:
    """Create the onboarding and lookup tables if they do not exist."""
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS EmployeeOnboarding (
            RequestId TEXT PRIMARY KEY,
            EmployeeName TEXT NOT NULL,
            JoinDate TEXT NOT NULL,
            Manager TEXT NOT NULL,
            Department TEXT NOT NULL,
            Location TEXT NOT NULL,
            LaptopRequired TEXT NOT NULL,
            VPNRequired TEXT NOT NULL,
            Status TEXT NOT NULL,
            CreatedDate TEXT NOT NULL,
            EmployeeId TEXT,
            FirstName TEXT NOT NULL,
            LastName TEXT NOT NULL,
            PersonalEmail TEXT NOT NULL,
            OfficialEmail TEXT,
            MobileNumber TEXT NOT NULL,
            EmployeeType TEXT NOT NULL,
            JobTitle TEXT NOT NULL,
            CostCenter TEXT NOT NULL,
            ManagerEmail TEXT NOT NULL,
            SkipManager TEXT,
            Country TEXT NOT NULL,
            OfficeLocation TEXT NOT NULL,
            WorkMode TEXT NOT NULL,
            MobileDeviceRequired TEXT NOT NULL,
            SpecialApplicationAccess TEXT,
            SpecialAccommodationRequirements TEXT,
            SecurityClearanceRequirements TEXT,
            OtherComments TEXT
        );

        CREATE TABLE IF NOT EXISTS DraftOnboarding (
            Token TEXT PRIMARY KEY,
            Payload TEXT NOT NULL,
            CreatedDate TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Departments (
            Department TEXT PRIMARY KEY
        );

        CREATE TABLE IF NOT EXISTS OfficeLocations (
            Location TEXT PRIMARY KEY
        );
        """
    )
    _ensure_column(connection, "EmployeeOnboarding", "ManagerActionToken", "TEXT")
    _ensure_column(connection, "EmployeeOnboarding", "HrActionToken", "TEXT")
    connection.executemany(
        "INSERT OR IGNORE INTO Departments (Department) VALUES (?)",
        [(department,) for department in DEPARTMENTS],
    )
    connection.executemany(
        "INSERT OR IGNORE INTO OfficeLocations (Location) VALUES (?)",
        [(location,) for location in OFFICE_LOCATIONS],
    )
    connection.commit()


def _ensure_column(
    connection: sqlite3.Connection, table_name: str, column_name: str, column_type: str
) -> None:
    columns = {
        row["name"]
        for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    }
    if column_name not in columns:
        connection.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        )


def normalize_form(raw_values: dict[str, Iterable[str]]) -> dict[str, str]:
    """Convert parsed form values into expected onboarding fields."""
    return {
        field: next(iter(raw_values.get(field, ("",))), "").strip()
        for field in FORM_FIELDS
    }


def validate_request(data: dict[str, str]) -> list[str]:
    """Return validation errors for a submitted onboarding request."""
    errors = [
        field.replace("_", " ").title()
        for field in REQUIRED_FIELDS
        if not data.get(field)
    ]
    if data.get("employee_type") and data["employee_type"] not in EMPLOYEE_TYPES:
        errors.append("Employee Type must be a configured option")
    if data.get("department") and data["department"] not in DEPARTMENTS:
        errors.append("Department must be a configured option")
    if data.get("office_location") and data["office_location"] not in OFFICE_LOCATIONS:
        errors.append("Office Location must be a configured option")
    if data.get("work_mode") and data["work_mode"] not in WORK_MODES:
        errors.append("Work Mode must be a configured option")
    for field in ("laptop_required", "mobile_device_required", "vpn_required"):
        if data.get(field) and data[field] not in ("Yes", "No"):
            errors.append(f"{field.replace('_', ' ').title()} must be Yes or No")
    return errors


def create_draft(connection: sqlite3.Connection, data: dict[str, str]) -> str:
    """Store reviewed form data server-side and return a submission token."""
    token = str(uuid.uuid4())
    created_date = datetime.now(timezone.utc).isoformat(timespec="seconds")
    connection.execute(
        """
        INSERT INTO DraftOnboarding (Token, Payload, CreatedDate)
        VALUES (?, ?, ?)
        """,
        (token, json.dumps(data), created_date),
    )
    connection.commit()
    return token


def get_draft(connection: sqlite3.Connection, token: str) -> dict[str, str] | None:
    """Return stored draft form data by token."""
    row = connection.execute(
        "SELECT Payload FROM DraftOnboarding WHERE Token = ?", (token,)
    ).fetchone()
    if row is None:
        return None
    payload = json.loads(row["Payload"])
    return {field: str(payload.get(field, "")) for field in FORM_FIELDS}


def delete_draft(connection: sqlite3.Connection, token: str) -> None:
    """Remove draft form data after edit or submit."""
    connection.execute("DELETE FROM DraftOnboarding WHERE Token = ?", (token,))
    connection.commit()


def create_onboarding_record(
    connection: sqlite3.Connection, data: dict[str, str]
) -> str:
    """Create an onboarding record and return its request ID."""
    errors = validate_request(data)
    if errors:
        raise ValueError("; ".join(errors))

    request_id = str(uuid.uuid4())
    manager_action_token = str(uuid.uuid4())
    hr_action_token = str(uuid.uuid4())
    created_date = datetime.now(timezone.utc).isoformat(timespec="seconds")
    employee_name = f"{data['first_name']} {data['last_name']}"
    connection.execute(
        """
        INSERT INTO EmployeeOnboarding (
            RequestId, EmployeeName, JoinDate, Manager, Department, Location,
            LaptopRequired, VPNRequired, Status, CreatedDate, EmployeeId,
            FirstName, LastName, PersonalEmail, OfficialEmail, MobileNumber,
            EmployeeType, JobTitle, CostCenter, ManagerEmail, SkipManager,
            Country, OfficeLocation, WorkMode, MobileDeviceRequired,
            SpecialApplicationAccess, SpecialAccommodationRequirements,
            SecurityClearanceRequirements, OtherComments, ManagerActionToken,
            HrActionToken
        ) VALUES (
            :RequestId, :EmployeeName, :JoinDate, :Manager, :Department, :Location,
            :LaptopRequired, :VPNRequired, :Status, :CreatedDate, :EmployeeId,
            :FirstName, :LastName, :PersonalEmail, :OfficialEmail, :MobileNumber,
            :EmployeeType, :JobTitle, :CostCenter, :ManagerEmail, :SkipManager,
            :Country, :OfficeLocation, :WorkMode, :MobileDeviceRequired,
            :SpecialApplicationAccess, :SpecialAccommodationRequirements,
            :SecurityClearanceRequirements, :OtherComments, :ManagerActionToken,
            :HrActionToken
        )
        """,
        {
            "RequestId": request_id,
            "EmployeeName": employee_name,
            "JoinDate": data["joining_date"],
            "Manager": data["manager_name"],
            "Department": data["department"],
            "Location": f"{data['country']} - {data['office_location']}",
            "LaptopRequired": data["laptop_required"],
            "VPNRequired": data["vpn_required"],
            "Status": "Submitted",
            "CreatedDate": created_date,
            "EmployeeId": data["employee_id"],
            "FirstName": data["first_name"],
            "LastName": data["last_name"],
            "PersonalEmail": data["personal_email"],
            "OfficialEmail": data["official_email"],
            "MobileNumber": data["mobile_number"],
            "EmployeeType": data["employee_type"],
            "JobTitle": data["job_title"],
            "CostCenter": data["cost_center"],
            "ManagerEmail": data["manager_email"],
            "SkipManager": data["skip_manager"],
            "Country": data["country"],
            "OfficeLocation": data["office_location"],
            "WorkMode": data["work_mode"],
            "MobileDeviceRequired": data["mobile_device_required"],
            "SpecialApplicationAccess": data["special_application_access"],
            "SpecialAccommodationRequirements": data[
                "special_accommodation_requirements"
            ],
            "SecurityClearanceRequirements": data[
                "security_clearance_requirements"
            ],
            "OtherComments": data["other_comments"],
            "ManagerActionToken": manager_action_token,
            "HrActionToken": hr_action_token,
        },
    )
    connection.commit()
    return request_id


def verify_action_token(
    request: sqlite3.Row, action: str, token: str
) -> bool:
    """Return True when the supplied action token matches the request."""
    token_column = {
        "manager": "ManagerActionToken",
        "hr": "HrActionToken",
    }[action]
    return bool(token) and request[token_column] == token


def get_request(connection: sqlite3.Connection, request_id: str) -> sqlite3.Row | None:
    """Return one onboarding request by ID."""
    return connection.execute(
        "SELECT * FROM EmployeeOnboarding WHERE RequestId = ?", (request_id,)
    ).fetchone()


def list_requests(connection: sqlite3.Connection) -> list[sqlite3.Row]:
    """Return all onboarding requests, newest first."""
    return list(
        connection.execute(
            """
            SELECT RequestId, EmployeeName, JoinDate, Manager, Department,
                   Location, LaptopRequired, VPNRequired, Status, CreatedDate
            FROM EmployeeOnboarding
            ORDER BY CreatedDate DESC
            """
        )
    )


def update_status(
    connection: sqlite3.Connection, request_id: str, status: str, token: str = ""
) -> bool:
    """Update a request status when the transition is allowed."""
    if status not in STATUSES:
        raise ValueError(f"Unknown status: {status}")

    current = get_request(connection, request_id)
    if current is None:
        return False

    required_action = "hr" if status == "Onboarding Ready" else "manager"
    if not verify_action_token(current, required_action, token):
        raise PermissionError("Invalid or missing action token")

    allowed = {
        "Submitted": {"Manager Approved", "Rejected"},
        "Manager Approved": {"Onboarding Ready"},
        "Rejected": set(),
        "Onboarding Ready": set(),
    }
    if status not in allowed[current["Status"]]:
        raise ValueError(f"Cannot change status from {current['Status']} to {status}")

    connection.execute(
        "UPDATE EmployeeOnboarding SET Status = ? WHERE RequestId = ?",
        (status, request_id),
    )
    connection.commit()
    return True


def render_page(title: str, body: str) -> bytes:
    """Return a complete HTML page."""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; background: #f7f8fb; }}
    main {{ max-width: 980px; margin: auto; background: white; padding: 2rem; border-radius: 12px; }}
    label {{ display: block; margin: 0.7rem 0; font-weight: 600; }}
    input, select, textarea {{ width: 100%; padding: 0.5rem; margin-top: 0.2rem; }}
    button, .button {{ background: #0757d3; color: white; border: 0; border-radius: 6px; padding: 0.7rem 1rem; text-decoration: none; display: inline-block; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
    th, td {{ border: 1px solid #ddd; padding: 0.6rem; text-align: left; }}
    th {{ background: #eef3ff; }}
    .actions {{ display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 1rem; }}
    .error {{ background: #ffecec; border: 1px solid #db5959; padding: 1rem; }}
  </style>
</head>
<body><main>
{body}
</main></body>
</html>""".encode()


def field(name: str, label: str, value: str = "", required: bool = False) -> str:
    marker = " required" if required else ""
    return (
        f'<label>{html.escape(label)}'
        f'<input name="{name}" value="{html.escape(value)}"{marker}></label>'
    )


def select_field(
    name: str, label: str, options: Iterable[str], value: str = "", required: bool = True
) -> str:
    marker = " required" if required else ""
    option_html = "".join(
        f'<option value="{html.escape(option)}"'
        f'{" selected" if option == value else ""}>{html.escape(option)}</option>'
        for option in options
    )
    return (
        f'<label>{html.escape(label)}<select name="{name}"{marker}>'
        f'<option value="">Select</option>{option_html}</select></label>'
    )


def textarea(name: str, label: str, value: str = "") -> str:
    return (
        f'<label>{html.escape(label)}'
        f'<textarea name="{name}">{html.escape(value)}</textarea></label>'
    )


def render_dashboard() -> bytes:
    return render_page(
        "Onboarding Dashboard",
        """
        <h1>Employee Onboarding Dashboard</h1>
        <div class="actions">
          <a class="button" href="/new">New Onboarding</a>
          <a class="button" href="/requests">My Requests</a>
        </div>
        """,
    )


def render_form(data: dict[str, str] | None = None, errors: list[str] | None = None) -> bytes:
    data = data or {field_name: "" for field_name in FORM_FIELDS}
    error_html = ""
    if errors:
        items = "".join(f"<li>{html.escape(error)}</li>" for error in errors)
        error_html = f'<div class="error"><strong>Please fix:</strong><ul>{items}</ul></div>'
    return render_page(
        "New Employee Form",
        f"""
        <h1>New Employee Form</h1>
        {error_html}
        <form method="post" action="/review">
          <h2>Employee Information</h2>
          {field("employee_id", "Employee ID", data["employee_id"])}
          {field("first_name", "First Name", data["first_name"], True)}
          {field("last_name", "Last Name", data["last_name"], True)}
          {field("personal_email", "Personal Email", data["personal_email"], True)}
          {field("official_email", "Official Email", data["official_email"])}
          {field("mobile_number", "Mobile Number", data["mobile_number"], True)}

          <h2>Employment Details</h2>
          {field("joining_date", "Joining Date", data["joining_date"], True)}
          {select_field("employee_type", "Employee Type", EMPLOYEE_TYPES, data["employee_type"])}
          {select_field("department", "Department", DEPARTMENTS, data["department"])}
          {field("job_title", "Job Title", data["job_title"], True)}
          {field("cost_center", "Cost Center", data["cost_center"], True)}

          <h2>Reporting Details</h2>
          {field("manager_name", "Manager Name", data["manager_name"], True)}
          {field("manager_email", "Manager Email", data["manager_email"], True)}
          {field("skip_manager", "Skip Manager", data["skip_manager"])}

          <h2>Location Details</h2>
          {field("country", "Country", data["country"], True)}
          {select_field("office_location", "Office Location", OFFICE_LOCATIONS, data["office_location"])}
          {select_field("work_mode", "Work Mode", WORK_MODES, data["work_mode"])}

          <h2>Access Requirements</h2>
          {select_field("laptop_required", "Laptop Required", ("Yes", "No"), data["laptop_required"])}
          {select_field("mobile_device_required", "Mobile Device Required", ("Yes", "No"), data["mobile_device_required"])}
          {select_field("vpn_required", "VPN Required", ("Yes", "No"), data["vpn_required"])}

          <h2>Additional Notes</h2>
          {textarea("special_application_access", "Special Application Access", data["special_application_access"])}
          {textarea("special_accommodation_requirements", "Special Accommodation Requirements", data["special_accommodation_requirements"])}
          {textarea("security_clearance_requirements", "Security Clearance Requirements", data["security_clearance_requirements"])}
          {textarea("other_comments", "Other Comments", data["other_comments"])}
          <button type="submit">Review</button>
        </form>
        """,
    )


def render_review(token: str, data: dict[str, str]) -> bytes:
    rows = (
        ("Employee Details", f"{data['first_name']} {data['last_name']}"),
        ("Employment Details", f"{data['employee_type']} - {data['department']} - {data['job_title']}"),
        ("Manager Details", f"{data['manager_name']} ({data['manager_email']})"),
        ("Asset Requirements", f"Laptop: {data['laptop_required']}; Mobile: {data['mobile_device_required']}"),
        ("Access Requirements", f"VPN: {data['vpn_required']}; Apps: {data['special_application_access'] or 'None'}"),
    )
    hidden = f'<input type="hidden" name="token" value="{html.escape(token)}">'
    table_rows = "".join(
        f"<tr><th>{html.escape(label)}</th><td>{html.escape(value)}</td></tr>"
        for label, value in rows
    )
    return render_page(
        "Review & Submit",
        f"""
        <h1>Review & Submit</h1>
        <table>{table_rows}</table>
        <div class="actions">
          <form method="post" action="/submit">{hidden}<button type="submit">Submit</button></form>
          <form method="post" action="/edit">{hidden}<button type="submit">Edit</button></form>
        </div>
        """,
    )


def render_requests(connection: sqlite3.Connection) -> bytes:
    rows = list_requests(connection)
    row_html = "".join(
        f"""
        <tr>
          <td><a href="/status/{row['RequestId']}">{html.escape(row['RequestId'][:8])}</a></td>
          <td>{html.escape(row['EmployeeName'])}</td>
          <td>{html.escape(row['JoinDate'])}</td>
          <td>{html.escape(row['Manager'])}</td>
          <td>{html.escape(row['Department'])}</td>
          <td>{html.escape(row['Status'])}</td>
        </tr>
        """
        for row in rows
    ) or '<tr><td colspan="6">No onboarding requests yet.</td></tr>'
    return render_page(
        "My Requests",
        f"""
        <h1>My Requests</h1>
        <table>
          <tr><th>Request</th><th>Employee</th><th>Join Date</th><th>Manager</th><th>Department</th><th>Status</th></tr>
          {row_html}
        </table>
        <p><a href="/">Back to dashboard</a></p>
        """,
    )


def render_status(
    connection: sqlite3.Connection,
    request_id: str,
    message: str = "",
    action_token: str = "",
) -> bytes:
    request = get_request(connection, request_id)
    if request is None:
        return render_page("Not Found", "<h1>Request not found</h1>")

    actions = ""
    if (
        request["Status"] == "Submitted"
        and verify_action_token(request, "manager", action_token)
    ):
        actions = f"""
        <form method="post" action="/manager/{request_id}">
          <input type="hidden" name="token" value="{html.escape(action_token)}">
          <button name="decision" value="approve" type="submit">Manager Approve</button>
          <button name="decision" value="reject" type="submit">Manager Reject</button>
        </form>
        """
    elif (
        request["Status"] == "Manager Approved"
        and verify_action_token(request, "hr", action_token)
    ):
        actions = f"""
        <form method="post" action="/hr/{request_id}">
          <input type="hidden" name="token" value="{html.escape(action_token)}">
          <button type="submit">Ready for Onboarding</button>
        </form>
        """
    message_html = f"<p><strong>{html.escape(message)}</strong></p>" if message else ""
    return render_page(
        "Request Status",
        f"""
        <h1>Request Status</h1>
        {message_html}
        <table>
          <tr><th>Request ID</th><td>{html.escape(request['RequestId'])}</td></tr>
          <tr><th>Employee</th><td>{html.escape(request['EmployeeName'])}</td></tr>
          <tr><th>Submitted</th><td>{html.escape(request['CreatedDate'])}</td></tr>
          <tr><th>Status</th><td>{html.escape(request['Status'])}</td></tr>
          <tr><th>Manager</th><td>{html.escape(request['Manager'])}</td></tr>
          <tr><th>Department</th><td>{html.escape(request['Department'])}</td></tr>
          <tr><th>Location</th><td>{html.escape(request['Location'])}</td></tr>
        </table>
        <div class="actions">{actions}</div>
        <p><a href="/requests">All requests</a></p>
        """,
    )


class OnboardingHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the onboarding application."""

    db_path = DB_PATH

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        with connect(self.db_path) as connection:
            init_db(connection)
            if parsed.path == "/":
                self.respond(render_dashboard())
            elif parsed.path == "/new":
                self.respond(render_form())
            elif parsed.path == "/requests":
                self.respond(render_requests(connection))
            elif parsed.path.startswith("/status/"):
                self.respond(
                    render_status(
                        connection,
                        parsed.path.removeprefix("/status/"),
                        action_token=query.get("token", [""])[0],
                    )
                )
            elif parsed.path.startswith("/manager/"):
                request_id = parsed.path.removeprefix("/manager/")
                self.respond(
                    render_status(
                        connection,
                        request_id,
                        "Manager approval screen.",
                        action_token=query.get("token", [""])[0],
                    )
                )
            elif parsed.path.startswith("/hr/"):
                request_id = parsed.path.removeprefix("/hr/")
                self.respond(
                    render_status(
                        connection,
                        request_id,
                        "HR final confirmation screen.",
                        action_token=query.get("token", [""])[0],
                    )
                )
            else:
                self.respond(render_page("Not Found", "<h1>Page not found</h1>"), 404)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode()
        data = normalize_form(parse_qs(raw_body))
        parsed_body = parse_qs(raw_body)

        if self.path == "/review":
            errors = validate_request(data)
            if errors:
                self.respond(render_form(data, errors))
            else:
                with connect(self.db_path) as connection:
                    init_db(connection)
                    self.respond(render_review(create_draft(connection, data), data))
        elif self.path == "/edit":
            token = next(iter(parsed_body.get("token", ("",))), "")
            with connect(self.db_path) as connection:
                init_db(connection)
                draft = get_draft(connection, token)
                if draft is None:
                    self.respond(render_page("Not Found", "<h1>Draft not found</h1>"), 404)
                else:
                    delete_draft(connection, token)
                    self.respond(render_form(draft))
        elif self.path == "/submit":
            token = next(iter(parsed_body.get("token", ("",))), "")
            with connect(self.db_path) as connection:
                init_db(connection)
                data = get_draft(connection, token)
                if data is None:
                    self.respond(render_page("Not Found", "<h1>Draft not found</h1>"), 404)
                    return
                try:
                    request_id = create_onboarding_record(connection, data)
                except ValueError as error:
                    self.respond(render_form(data, str(error).split("; ")), 400)
                else:
                    delete_draft(connection, token)
                    request = get_request(connection, request_id)
                    manager_url = (
                        f"/manager/{request_id}?token={request['ManagerActionToken']}"
                    )
                    self.respond(
                        render_status(
                            connection,
                            request_id,
                            "Request submitted. Share the manager approval link: "
                            + manager_url,
                        )
                    )
        elif self.path.startswith("/manager/"):
            request_id = self.path.removeprefix("/manager/")
            token = next(iter(parsed_body.get("token", ("",))), "")
            decision = next(iter(parsed_body.get("decision", ("",))), "")
            status = "Manager Approved" if decision == "approve" else "Rejected"
            with connect(self.db_path) as connection:
                init_db(connection)
                try:
                    update_status(connection, request_id, status, token)
                except (PermissionError, ValueError) as error:
                    self.respond(render_status(connection, request_id, str(error)), 400)
                else:
                    request = get_request(connection, request_id)
                    hr_url = f"/hr/{request_id}?token={request['HrActionToken']}"
                    message = f"Status updated to {status}."
                    if status == "Manager Approved":
                        message += " Share the HR confirmation link: " + hr_url
                    self.respond(render_status(connection, request_id, message))
        elif self.path.startswith("/hr/"):
            request_id = self.path.removeprefix("/hr/")
            token = next(iter(parsed_body.get("token", ("",))), "")
            with connect(self.db_path) as connection:
                init_db(connection)
                try:
                    update_status(connection, request_id, "Onboarding Ready", token)
                except (PermissionError, ValueError) as error:
                    self.respond(render_status(connection, request_id, str(error)), 400)
                else:
                    self.respond(
                        render_status(
                            connection,
                            request_id,
                            "Status updated to Onboarding Ready.",
                        )
                    )
        else:
            self.respond(render_page("Not Found", "<h1>Page not found</h1>"), 404)

    def respond(self, body: bytes, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Start the onboarding application server."""
    with connect(DB_PATH) as connection:
        init_db(connection)
    server = ThreadingHTTPServer((host, port), OnboardingHandler)
    print(f"Employee onboarding app running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
