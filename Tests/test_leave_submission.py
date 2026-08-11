from datetime import date, timedelta
import pytest
from app.models import LeaveRequest


def test_get_apply_page(client):
    """Verify application form page loads successfully."""
    response = client.get("/apply")
    assert response.status_code == 200
    assert b"Submit Leave Request" in response.data


def test_valid_leave_request_submission(client, app):
    """Positive Test 1: Valid leave request is created via HTTP POST."""
    today = date.today()
    start_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=3)).strftime("%Y-%m-%d")

    response = client.post(
        "/apply",
        data={
            "employee_name": "Laura Croft",
            "start_date": start_date,
            "end_date": end_date,
            "reason": "Rest and relaxation",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Leave request submitted successfully." in response.data

    with app.app_context():
        leave_req = LeaveRequest.query.filter_by(employee_name="Laura Croft").first()
        assert leave_req is not None
        assert leave_req.status == "PENDING"
        assert leave_req.duration_days == 3


def test_valid_5_day_leave_accepted(client, app):
    """Positive Test 2: Valid 5-day leave without reason is accepted."""
    today = date.today()
    start_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")  # 5 days

    response = client.post(
        "/apply",
        data={
            "employee_name": "Michael Scott",
            "start_date": start_date,
            "end_date": end_date,
            "reason": "",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Leave request submitted successfully." in response.data

    with app.app_context():
        leave_req = LeaveRequest.query.filter_by(employee_name="Michael Scott").first()
        assert leave_req is not None
        assert leave_req.duration_days == 5


def test_valid_10_day_leave_with_reason_accepted(client, app):
    """Positive Test 3: Valid 10-day leave with reason is accepted."""
    today = date.today()
    start_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=10)).strftime("%Y-%m-%d")  # 10 days

    response = client.post(
        "/apply",
        data={
            "employee_name": "Nancy Drew",
            "start_date": start_date,
            "end_date": end_date,
            "reason": "Annual vacation and personal research",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Leave request submitted successfully." in response.data

    with app.app_context():
        leave_req = LeaveRequest.query.filter_by(employee_name="Nancy Drew").first()
        assert leave_req is not None
        assert leave_req.duration_days == 10


def test_invalid_submission_returns_400(client):
    """Integration Test: Invalid form submission returns HTTP 400."""
    today = date.today()
    past_date = (today - timedelta(days=2)).strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")

    response = client.post(
        "/apply",
        data={
            "employee_name": "Oscar Martinez",
            "start_date": past_date,
            "end_date": end_date,
            "reason": "",
        },
    )
    assert response.status_code == 400
    assert b"Start date cannot be in the past" in response.data
