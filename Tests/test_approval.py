from datetime import date, timedelta
import pytest
from app import db
from app.models import LeaveRequest
from app.services import create_leave_request


def test_manager_approve_pending_request(client, app):
    """Positive Test 4: Manager can approve a pending request."""
    today = date.today()
    with app.app_context():
        leave_req, _ = create_leave_request(
            "Pam Beesly",
            today + timedelta(days=1),
            today + timedelta(days=3),
            "Personal",
        )
        leave_id = leave_req.id

    response = client.post(
        f"/leave/{leave_id}/approve",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"approved successfully" in response.data

    with app.app_context():
        updated_req = db.session.get(LeaveRequest, leave_id)
        assert updated_req.status == "APPROVED"


def test_manager_reject_pending_request(client, app):
    """Positive Test 5: Manager can reject a pending request."""
    today = date.today()
    with app.app_context():
        leave_req, _ = create_leave_request(
            "Quentin Tarantino",
            today + timedelta(days=1),
            today + timedelta(days=2),
            "Event",
        )
        leave_id = leave_req.id

    response = client.post(
        f"/leave/{leave_id}/reject",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"rejected successfully" in response.data

    with app.app_context():
        updated_req = db.session.get(LeaveRequest, leave_id)
        assert updated_req.status == "REJECTED"


def test_approve_nonexistent_leave_request(client):
    """Negative Test 12: Approving nonexistent leave request returns 404."""
    response = client.post("/leave/99999/approve")
    assert response.status_code == 404
    assert b"does not exist" in response.data


def test_reject_nonexistent_leave_request(client):
    """Negative Test 13: Rejecting nonexistent leave request returns 404."""
    response = client.post("/leave/99999/reject")
    assert response.status_code == 404
    assert b"does not exist" in response.data


def test_approving_already_rejected_request(client, app):
    """Negative Test 14: Approving an already rejected request fails (returns 400)."""
    today = date.today()
    with app.app_context():
        leave_req, _ = create_leave_request(
            "Rachel Green",
            today + timedelta(days=1),
            today + timedelta(days=2),
            "Personal",
        )
        leave_id = leave_req.id

    # First reject the request
    client.post(f"/leave/{leave_id}/reject")

    # Attempt to approve the already REJECTED request
    response = client.post(f"/leave/{leave_id}/approve")
    assert response.status_code == 400
    assert b"Cannot approve request in status &#39;REJECTED&#39;" in response.data or b"Cannot approve request in status 'REJECTED'" in response.data


def test_rejecting_already_approved_request(client, app):
    """Negative Test 15: Rejecting an already approved request fails (returns 400)."""
    today = date.today()
    with app.app_context():
        leave_req, _ = create_leave_request(
            "Steven Hyde",
            today + timedelta(days=1),
            today + timedelta(days=2),
            "Personal",
        )
        leave_id = leave_req.id

    # First approve the request
    client.post(f"/leave/{leave_id}/approve")

    # Attempt to reject the already APPROVED request
    response = client.post(f"/leave/{leave_id}/reject")
    assert response.status_code == 400
    assert b"Cannot reject request in status &#39;APPROVED&#39;" in response.data or b"Cannot reject request in status 'APPROVED'" in response.data
