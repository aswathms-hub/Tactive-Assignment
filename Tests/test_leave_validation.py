from datetime import date, timedelta
import pytest
from app.services import create_leave_request, validate_leave_request


def test_empty_employee_name(app):
    """Negative Test 6: Empty employee name fails validation."""
    today = date.today()
    is_valid, errors = validate_leave_request("", today, today + timedelta(days=2))
    assert not is_valid
    assert any("Employee name is required" in err for err in errors)

    is_valid_space, errors_space = validate_leave_request(
        "   ", today, today + timedelta(days=2)
    )
    assert not is_valid_space
    assert any("Employee name is required" in err for err in errors_space)


def test_past_start_date(app):
    """Negative Test 7: Past start date fails validation."""
    past_date = date.today() - timedelta(days=1)
    end_date = date.today() + timedelta(days=2)
    is_valid, errors = validate_leave_request("Alice Smith", past_date, end_date)
    assert not is_valid
    assert any("Start date cannot be in the past" in err for err in errors)


def test_end_date_before_start_date(app):
    """Negative Test 8: End date before start date fails validation."""
    today = date.today()
    start_date = today + timedelta(days=5)
    end_date = today + timedelta(days=3)
    is_valid, errors = validate_leave_request("Bob Jones", start_date, end_date)
    assert not is_valid
    assert any(
        "End date must be the same as or later than start date" in err for err in errors
    )


def test_leave_duration_exceeds_max_10_days(app):
    """Negative Test 9: Duration > 10 calendar days fails validation."""
    today = date.today()
    start_date = today + timedelta(days=1)
    end_date = start_date + timedelta(days=11)  # 12 days total
    is_valid, errors = validate_leave_request(
        "Charlie Brown", start_date, end_date, reason="Vacation trip"
    )
    assert not is_valid
    assert any("cannot exceed 10 calendar days" in err for err in errors)


def test_more_than_5_days_without_reason(app):
    """Negative Test 10: >5 days leave without reason fails validation."""
    today = date.today()
    start_date = today + timedelta(days=1)
    end_date = start_date + timedelta(days=5)  # 6 days total
    is_valid, errors = validate_leave_request(
        "Diana Prince", start_date, end_date, reason=""
    )
    assert not is_valid
    assert any("A reason is required" in err for err in errors)


def test_overlapping_leave_request(app):
    """Negative Test 11: Overlapping leave request fails validation."""
    today = date.today()
    start1 = today + timedelta(days=2)
    end1 = start1 + timedelta(days=3)  # 4 days

    # Create initial leave request
    req1, errors1 = create_leave_request(
        "Edward Elric", start1, end1, reason="Personal"
    )
    assert req1 is not None
    assert len(errors1) == 0

    # Attempt overlapping leave request (start inside existing range)
    start2 = start1 + timedelta(days=1)
    end2 = start2 + timedelta(days=2)
    is_valid, errors2 = validate_leave_request("Edward Elric", start2, end2)
    assert not is_valid
    assert any("Overlapping leave request found" in err for err in errors2)

    # Attempt overlapping leave request (enclosing existing range)
    start3 = start1 - timedelta(days=1)
    end3 = end1 + timedelta(days=1)
    is_valid3, errors3 = validate_leave_request("Edward Elric", start3, end3)
    assert not is_valid3
    assert any("Overlapping leave request found" in err for err in errors3)


def test_boundary_one_day_leave(app):
    """Boundary Test 16: One-day leave is accepted without reason."""
    today = date.today()
    start_date = today + timedelta(days=1)
    end_date = start_date  # 1 day duration
    is_valid, errors = validate_leave_request("Fiona Apple", start_date, end_date, "")
    assert is_valid
    assert len(errors) == 0


def test_boundary_five_day_leave_without_reason(app):
    """Boundary Test 17: Exactly 5-day leave without reason is accepted."""
    today = date.today()
    start_date = today + timedelta(days=1)
    end_date = start_date + timedelta(days=4)  # 5 days duration
    is_valid, errors = validate_leave_request("George Clark", start_date, end_date, "")
    assert is_valid
    assert len(errors) == 0


def test_boundary_six_day_leave_without_reason(app):
    """Boundary Test 18: 6-day leave without reason is rejected."""
    today = date.today()
    start_date = today + timedelta(days=1)
    end_date = start_date + timedelta(days=5)  # 6 days duration
    is_valid, errors = validate_leave_request(
        "Hannah Abbott", start_date, end_date, ""
    )
    assert not is_valid
    assert any("A reason is required" in err for err in errors)


def test_boundary_six_day_leave_with_reason(app):
    """Boundary Test 19: 6-day leave with reason is accepted."""
    today = date.today()
    start_date = today + timedelta(days=1)
    end_date = start_date + timedelta(days=5)  # 6 days duration
    is_valid, errors = validate_leave_request(
        "Ian Malcolm", start_date, end_date, "Family function"
    )
    assert is_valid
    assert len(errors) == 0


def test_boundary_ten_day_leave_with_reason(app):
    """Boundary Test 20: Exactly 10-day leave with reason is accepted."""
    today = date.today()
    start_date = today + timedelta(days=1)
    end_date = start_date + timedelta(days=9)  # 10 days duration
    is_valid, errors = validate_leave_request(
        "Julia Roberts", start_date, end_date, "Annual holiday"
    )
    assert is_valid
    assert len(errors) == 0


def test_boundary_eleven_day_leave(app):
    """Boundary Test 21: 11-day leave is rejected."""
    today = date.today()
    start_date = today + timedelta(days=1)
    end_date = start_date + timedelta(days=10)  # 11 days duration
    is_valid, errors = validate_leave_request(
        "Kevin Bacon", start_date, end_date, "Long trip"
    )
    assert not is_valid
    assert any("cannot exceed 10 calendar days" in err for err in errors)
