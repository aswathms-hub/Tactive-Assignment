from datetime import date
from typing import List, Tuple
from app import db
from app.models import LeaveRequest

# Configurable business limits
MAX_LEAVE_DAYS = 10
MAX_REASONLESS_DAYS = 5


def validate_leave_request(
    employee_name: str, start_date: date, end_date: date, reason: str = ""
) -> Tuple[bool, List[str]]:
    """
    Validates leave request against business rules 1-6.
    Returns (is_valid, list_of_error_messages).
    """
    errors = []

    # Rule 1 — Required employee name
    if not employee_name or not employee_name.strip():
        errors.append("Employee name is required.")

    # Rule 2 — Start date cannot be in the past
    today = date.today()
    if start_date and start_date < today:
        errors.append("Start date cannot be in the past.")

    # Rule 3 — End date validation
    if start_date and end_date and end_date < start_date:
        errors.append("End date must be the same as or later than start date.")

    # Rules 4 & 5 rely on valid start and end date logic
    if start_date and end_date and end_date >= start_date:
        duration = (end_date - start_date).days + 1

        # Rule 4 — Maximum leave duration (<= 10 days)
        if duration > MAX_LEAVE_DAYS:
            errors.append(
                f"Leave duration cannot exceed {MAX_LEAVE_DAYS} calendar days."
            )

        # Rule 5 — Reason requirement (> 5 days requires reason)
        if duration > MAX_REASONLESS_DAYS and (not reason or not reason.strip()):
            errors.append(
                f"A reason is required for leave requests longer than {MAX_REASONLESS_DAYS} days."
            )

        # Rule 6 — No overlapping leave (PENDING or APPROVED)
        if employee_name and employee_name.strip():
            clean_name = employee_name.strip()
            overlapping = LeaveRequest.query.filter(
                db.func.lower(LeaveRequest.employee_name) == clean_name.lower(),
                LeaveRequest.status.in_(["PENDING", "APPROVED"]),
                LeaveRequest.start_date <= end_date,
                LeaveRequest.end_date >= start_date,
            ).first()

            if overlapping:
                errors.append(
                    f"Overlapping leave request found for '{clean_name}' "
                    f"({overlapping.start_date} to {overlapping.end_date}, Status: {overlapping.status})."
                )

    is_valid = len(errors) == 0
    return is_valid, errors


def create_leave_request(
    employee_name: str, start_date: date, end_date: date, reason: str = ""
) -> Tuple[LeaveRequest | None, List[str]]:
    """
    Creates a new leave request if validation passes.
    Returns (LeaveRequest, list_of_errors).
    """
    cleaned_name = employee_name.strip() if employee_name else ""
    cleaned_reason = reason.strip() if reason else ""

    is_valid, errors = validate_leave_request(
        cleaned_name, start_date, end_date, cleaned_reason
    )

    if not is_valid:
        return None, errors

    leave_req = LeaveRequest(
        employee_name=cleaned_name,
        start_date=start_date,
        end_date=end_date,
        reason=cleaned_reason if cleaned_reason else None,
        status="PENDING",
    )

    try:
        db.session.add(leave_req)
        db.session.commit()
        return leave_req, []
    except Exception as e:
        db.session.rollback()
        return None, [f"Database error occurred: {str(e)}"]


def approve_leave_request(leave_id: int) -> Tuple[LeaveRequest | None, str]:
    """
    Approves a PENDING leave request.
    Returns (updated_request, message).
    """
    if not isinstance(leave_id, int) or leave_id <= 0:
        raise ValueError("Invalid leave request ID.")

    leave_req = db.session.get(LeaveRequest, leave_id)
    if not leave_req:
        raise ValueError(f"Leave request with ID {leave_id} does not exist.")

    if leave_req.status != "PENDING":
        raise ValueError(
            f"Cannot approve request in status '{leave_req.status}'. Only PENDING requests can be approved."
        )

    leave_req.status = "APPROVED"
    try:
        db.session.commit()
        return (
            leave_req,
            f"Leave request #{leave_req.id} for {leave_req.employee_name} approved successfully.",
        )
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Database update failed: {str(e)}")


def reject_leave_request(leave_id: int) -> Tuple[LeaveRequest | None, str]:
    """
    Rejects a PENDING leave request.
    Returns (updated_request, message).
    """
    if not isinstance(leave_id, int) or leave_id <= 0:
        raise ValueError("Invalid leave request ID.")

    leave_req = db.session.get(LeaveRequest, leave_id)
    if not leave_req:
        raise ValueError(f"Leave request with ID {leave_id} does not exist.")

    if leave_req.status != "PENDING":
        raise ValueError(
            f"Cannot reject request in status '{leave_req.status}'. Only PENDING requests can be rejected."
        )

    leave_req.status = "REJECTED"
    try:
        db.session.commit()
        return (
            leave_req,
            f"Leave request #{leave_req.id} for {leave_req.employee_name} rejected successfully.",
        )
    except Exception as e:
        db.session.rollback()
        raise RuntimeError(f"Database update failed: {str(e)}")


def get_all_leave_requests() -> List[LeaveRequest]:
    return LeaveRequest.query.order_by(LeaveRequest.created_at.desc()).all()


def get_pending_leave_requests() -> List[LeaveRequest]:
    return (
        LeaveRequest.query.filter_by(status="PENDING")
        .order_by(LeaveRequest.created_at.asc())
        .all()
    )


def get_employee_leave_requests(employee_name: str) -> List[LeaveRequest]:
    if not employee_name:
        return []
    return (
        LeaveRequest.query.filter(
            db.func.lower(LeaveRequest.employee_name) == employee_name.strip().lower()
        )
        .order_by(LeaveRequest.created_at.desc())
        .all()
    )
