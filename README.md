# Smart Leave Approval System

An automated, server-validated, web application built with Flask, SQLAlchemy, SQLite, Bootstrap 5, and pytest to manage employee leave requests and manager approvals.

---

## 1. Problem Statement

Manual leave approval processes often lead to scheduling conflicts, policy violations (such as excessive leave duration or unexcused extended absences), and invalid date entries. The **Smart Leave Approval System** provides a reliable web application where employees can submit leave requests subject to automated business validation rules, and managers can easily review, approve, or reject pending requests.

---

## 2. Features

- **Employee Submission Interface**: Form to submit leave requests with employee name, start date, end date, and reason.
- **Server-Side Rule Engine**: 6 strict business rules validated on the server before persisting requests.
- **Employee Request Log**: View all submitted leave requests along with real-time status badges (`PENDING`, `APPROVED`, `REJECTED`).
- **Manager Approval Dashboard**: Dedicated view listing pending requests with one-click **Approve** and **Reject** actions.
- **State-Transition Integrity**: Strict control flows preventing state mutations on non-existent or previously finalized requests.
- **Automated Test Suite**: 23 pytest test cases covering positive, negative, and boundary scenarios.
- **Deliberate Mutation Testing**: Verification of test suite defect-detection capability through intentional code mutation.

---

## 3. Architecture

The application follows the **Flask Application Factory Pattern** combined with a decoupled service layer architecture:

```
[ Web Browser / Client ]
          │
          ▼
 [ Routes / Blueprint (app/routes.py) ]
          │
          ▼
[ Service Layer / Validation Rules (app/services.py) ]
          │
          ▼
[ ORM / Models (app/models.py) ]
          │
          ▼
  [ SQLite Database ]
```

---

## 4. Technology Stack

- **Python**: 3.11+
- **Framework**: Flask 3.1.2
- **ORM & Database**: Flask-SQLAlchemy 3.1.1 & SQLite
- **Frontend**: HTML5, Bootstrap 5.3.2, Bootstrap Icons
- **Test Framework**: pytest 9.0.3, pytest-flask 1.3.0
- **Configuration**: python-dotenv 1.2.2

---

## 5. Project Structure

```
smart-leave-system/
│
├── app/
│   ├── __init__.py          # Flask Application Factory & DB initialization
│   ├── models.py            # LeaveRequest SQLAlchemy model
│   ├── routes.py            # Flask HTTP route handlers & HTTP status code responses
│   ├── services.py          # Business logic validation engine & CRUD services
│   ├── templates/
│   │   ├── base.html        # Master Bootstrap 5 layout template
│   │   ├── index.html       # Overview dashboard & stats
│   │   ├── apply_leave.html # Employee leave application form
│   │   ├── requests.html    # Employee request listing & search view
│   │   └── manager.html     # Manager approval queue & history
│   └── static/
│       └── style.css        # Custom CSS styling & UI enhancements
│
├── tests/
│   ├── conftest.py          # Pytest fixtures (Flask app & in-memory SQLite DB)
│   ├── test_leave_validation.py # Unit tests for Rules 1-6 & boundary cases
│   ├── test_leave_submission.py # Integration tests for POST /apply
│   └── test_approval.py     # Integration tests for approval/rejection routes
│
├── .gitignore               # Ignored files (DB, pycache, venv)
├── requirements.txt         # Pinned python dependencies
├── README.md                # Complete system documentation
└── run.py                   # Application entry point script
```

---

## 6. Business Rules

The application enforces the following rules strictly on the server side:

- **Rule 1 — Required Employee Name**: Name cannot be empty or contain only whitespace.
- **Rule 2 — Start Date Validation**: Start date cannot be before today's date (`start_date >= date.today()`).
- **Rule 3 — End Date Validation**: End date must be the same as or later than start date (`end_date >= start_date`).
- **Rule 4 — Maximum Leave Duration**: Leave duration cannot exceed **10 calendar days** (`(end_date - start_date).days + 1 <= 10`).
- **Rule 5 — Reason Requirement**: If leave duration is greater than **5 calendar days**, a non-empty reason is mandatory.
- **Rule 6 — No Overlapping Leave**: An employee cannot submit a leave request that overlaps an existing `PENDING` or `APPROVED` leave request for that employee.
- **Rule 7 — Request Persistence**: Upon passing all validation rules, the request is stored in SQLite with status `PENDING`.

---

## 7. Installation Instructions

1. **Clone or navigate to the project directory**:
   ```bash
   cd c:/Users/User/OneDrive/Desktop/project2
   ```

2. **Create and activate a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   python -m pip install -r requirements.txt
   ```

---

## 8. How to Run the Application

Start the Flask development server by running:

```bash
python run.py
```

Open your browser and navigate to:
`http://127.0.0.1:5000`

---

## 9. How to Run Tests

Execute the pytest suite using:

```bash
python -m pytest -v
```

---

## 10. Expected Test Output

Running `python -m pytest -v` should produce:

```text
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\Users\User\OneDrive\Desktop\project2
plugins: anyio-4.11.0, flask-1.3.0
collected 23 items

tests/test_approval.py::test_manager_approve_pending_request PASSED      [  4%]
tests/test_approval.py::test_manager_reject_pending_request PASSED       [  8%]
tests/test_approval.py::test_approve_nonexistent_leave_request PASSED    [ 13%]
tests/test_approval.py::test_reject_nonexistent_leave_request PASSED     [ 17%]
tests/test_approval.py::test_approving_already_rejected_request PASSED   [ 21%]
tests/test_approval.py::test_rejecting_already_approved_request PASSED   [ 26%]
tests/test_leave_submission.py::test_get_apply_page PASSED               [ 30%]
tests/test_leave_submission.py::test_valid_leave_request_submission PASSED [ 34%]
tests/test_leave_submission.py::test_valid_5_day_leave_accepted PASSED   [ 39%]
tests/test_leave_submission.py::test_valid_10_day_leave_with_reason_accepted PASSED [ 43%]
tests/test_leave_submission.py::test_invalid_submission_returns_400 PASSED [ 47%]
tests/test_leave_validation.py::test_empty_employee_name PASSED          [ 52%]
tests/test_leave_validation.py::test_past_start_date PASSED              [ 56%]
tests/test_leave_validation.py::test_end_date_before_start_date PASSED   [ 60%]
tests/test_leave_validation.py::test_leave_duration_exceeds_max_10_days PASSED [ 65%]
tests/test_leave_validation.py::test_more_than_5_days_without_reason PASSED [ 69%]
tests/test_leave_validation.py::test_overlapping_leave_request PASSED    [ 73%]
tests/test_leave_validation.py::test_boundary_one_day_leave PASSED       [ 78%]
tests/test_leave_validation.py::test_boundary_five_day_leave_without_reason PASSED [ 82%]
tests/test_leave_validation.py::test_boundary_six_day_leave_without_reason PASSED [ 86%]
tests/test_leave_validation.py::test_boundary_six_day_leave_with_reason PASSED [ 91%]
tests/test_leave_validation.py::test_boundary_ten_day_leave_with_reason PASSED [ 95%]
tests/test_leave_validation.py::test_boundary_eleven_day_leave PASSED    [100%]

============================= 23 passed in 1.61s ==============================
```

---

## 11. Deliberate Bug Demonstration (Mutation Testing)

To demonstrate that the test suite effectively catches regression bugs:

1. **Modify rule constant in [app/services.py](file:///c:/Users/User/OneDrive/Desktop/project2/app/services.py)**:
   ```python
   # Change from:
   MAX_LEAVE_DAYS = 10
   # To:
   MAX_LEAVE_DAYS = 15
   ```

2. **Execute pytest**:
   ```bash
   python -m pytest -v
   ```

3. **Captured Failing Output**:
   ```text
   ================================== FAILURES ===================================
   ___________________ test_leave_duration_exceeds_max_10_days ___________________
   >       assert not is_valid
   E       assert not True
   tests\test_leave_validation.py:49: AssertionError

   _______________________ test_boundary_eleven_day_leave ________________________
   >       assert not is_valid
   E       assert not True
   tests\test_leave_validation.py:157: AssertionError
   ======================== 2 failed, 21 passed in 1.99s =========================
   ```

4. **Restore `app/services.py`**:
   Set `MAX_LEAVE_DAYS = 10` again. Re-run `python -m pytest -v` to confirm all 23 tests pass.

---

## 12. AI Testing Workflow

The AI testing workflow follows a strict test-driven evaluation model:
1. **Rule Formalization**: Define rules in `services.py` as pure functions with standard signatures.
2. **Pytest Harnessing**: Create isolated unit and integration test fixtures using in-memory SQLite databases.
3. **Automated Verification**: Run tests after every change to catch regressions immediately.

---

## 13. AI Change-Loop Workflow

When introducing new requirements or modifying business rules:
1. **Plan & Specify**: Document proposed rule updates in an implementation plan.
2. **Update Service & Tests**: Add or modify test cases to reflect new constraints before updating business code.
3. **Execute & Verify**: Run `python -m pytest` to confirm green build status.

---

## 14. Security Considerations

- **Server-Side Input Validation**: Client input is never trusted. All date checks, length checks, and string sanitizations happen on the server.
- **SQL Injection Prevention**: Built entirely with SQLAlchemy ORM parameter binding (no string concatenation in queries).
- **Template XSS Protection**: Uses Jinja2 automatic HTML escaping for all dynamic data rendering.
- **State Transition Guard**: HTTP POST requests validate current status before mutating state (`PENDING` -> `APPROVED` / `REJECTED`).
- **Sanitizing Errors**: Internal database exceptions are logged and hidden from users behind user-friendly error banners.

---

## 15. Known Limitations

- **No User Authentication**: Employees and managers are unauthenticated in this minimal demonstration scope.
- **Single Currency/Calendar**: Does not account for public holidays or company weekend policies when calculating calendar duration.

---

## 16. Future Improvements (Suggested Stage 3 Feature)

**Suggested Stage 3 Feature**: *Leave Balance & Accrual Tracking*
- Add an `Employee` model with total annual leave quota (e.g., 20 days/year) and track remaining accrued leave balance.
- Automatically check and deduct leave balance upon manager approval.
