"# brd" 

## Employee onboarding application

This repository includes a self-contained Python web application for submitting
and tracking new employee onboarding requests.

### Run the app

```bash
python onboarding_app.py
```

Open `http://127.0.0.1:8000` in a browser.

### Workflow supported

- Dashboard with **New Onboarding** and **My Requests**
- New employee form capturing employee, employment, reporting, location, asset,
  access, and notes details
- Review and submit screen
- SQLite-backed `EmployeeOnboarding` table with lookup tables for departments
  and office locations
- Request status tracking:
  - Submitted
  - Manager Approved
  - Rejected
  - Onboarding Ready

### Run tests

```bash
python -m unittest
```"
