from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.models import LeaveRequest
from app.services import (
    approve_leave_request,
    create_leave_request,
    get_all_leave_requests,
    get_employee_leave_requests,
    get_pending_leave_requests,
    reject_leave_request,
)

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Home landing page / summary dashboard."""
    all_requests = get_all_leave_requests()
    stats = {
        "total": len(all_requests),
        "pending": sum(1 for r in all_requests if r.status == "PENDING"),
        "approved": sum(1 for r in all_requests if r.status == "APPROVED"),
        "rejected": sum(1 for r in all_requests if r.status == "REJECTED"),
    }
    recent_requests = all_requests[:5]
    return render_template("index.html", stats=stats, recent_requests=recent_requests)


@bp.route("/apply", methods=["GET", "POST"])
def apply_leave():
    """Employee leave application form."""
    if request.method == "POST":
        employee_name = request.form.get("employee_name", "").strip()
        start_date_str = request.form.get("start_date", "").strip()
        end_date_str = request.form.get("end_date", "").strip()
        reason = request.form.get("reason", "").strip()

        errors = []
        start_date = None
        end_date = None

        if not start_date_str:
            errors.append("Start date is required.")
        else:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                errors.append("Invalid start date format. Please use YYYY-MM-DD.")

        if not end_date_str:
            errors.append("End date is required.")
        else:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError:
                errors.append("Invalid end date format. Please use YYYY-MM-DD.")

        if not errors:
            leave_req, validation_errors = create_leave_request(
                employee_name=employee_name,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
            )
            if validation_errors:
                errors.extend(validation_errors)
            else:
                flash("Leave request submitted successfully.", "success")
                return redirect(
                    url_for("main.view_requests", employee_name=employee_name)
                ), 302

        # If validation fails, re-render with HTTP 400 Bad Request status code
        form_data = {
            "employee_name": employee_name,
            "start_date": start_date_str,
            "end_date": end_date_str,
            "reason": reason,
        }
        return (
            render_template("apply_leave.html", errors=errors, form_data=form_data),
            400,
        )

    return render_template("apply_leave.html", errors=[], form_data={})


@bp.route("/requests")
def view_requests():
    """Employee view showing submitted leave requests."""
    search_name = request.args.get("employee_name", "").strip()
    if search_name:
        requests_list = get_employee_leave_requests(search_name)
    else:
        requests_list = get_all_leave_requests()

    return render_template(
        "requests.html", requests_list=requests_list, search_name=search_name
    )


@bp.route("/manager")
def manager_dashboard():
    """Manager dashboard showing pending leave requests for approval/rejection."""
    pending_requests = get_pending_leave_requests()
    all_requests = get_all_leave_requests()
    return render_template(
        "manager.html",
        pending_requests=pending_requests,
        all_requests=all_requests,
    )


@bp.route("/leave/<leave_id_str>/approve", methods=["POST"])
def approve_leave(leave_id_str):
    """POST route to approve a leave request."""
    try:
        leave_id = int(leave_id_str)
    except (ValueError, TypeError):
        flash("Invalid leave request ID format.", "danger")
        return (
            render_template(
                "manager.html",
                pending_requests=get_pending_leave_requests(),
                all_requests=get_all_leave_requests(),
                error_msg="Invalid leave request ID.",
            ),
            400,
        )

    try:
        leave_req, success_msg = approve_leave_request(leave_id)
        flash(success_msg, "success")
        return redirect(url_for("main.manager_dashboard")), 302
    except ValueError as e:
        err_text = str(e)
        flash(err_text, "danger")
        status_code = 404 if "does not exist" in err_text else 400
        return (
            render_template(
                "manager.html",
                pending_requests=get_pending_leave_requests(),
                all_requests=get_all_leave_requests(),
                error_msg=err_text,
            ),
            status_code,
        )
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", "danger")
        return (
            render_template(
                "manager.html",
                pending_requests=get_pending_leave_requests(),
                all_requests=get_all_leave_requests(),
                error_msg="Database error.",
            ),
            500,
        )


@bp.route("/leave/<leave_id_str>/reject", methods=["POST"])
def reject_leave(leave_id_str):
    """POST route to reject a leave request."""
    try:
        leave_id = int(leave_id_str)
    except (ValueError, TypeError):
        flash("Invalid leave request ID format.", "danger")
        return (
            render_template(
                "manager.html",
                pending_requests=get_pending_leave_requests(),
                all_requests=get_all_leave_requests(),
                error_msg="Invalid leave request ID.",
            ),
            400,
        )

    try:
        leave_req, success_msg = reject_leave_request(leave_id)
        flash(success_msg, "success")
        return redirect(url_for("main.manager_dashboard")), 302
    except ValueError as e:
        err_text = str(e)
        flash(err_text, "danger")
        status_code = 404 if "does not exist" in err_text else 400
        return (
            render_template(
                "manager.html",
                pending_requests=get_pending_leave_requests(),
                all_requests=get_all_leave_requests(),
                error_msg=err_text,
            ),
            status_code,
        )
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", "danger")
        return (
            render_template(
                "manager.html",
                pending_requests=get_pending_leave_requests(),
                all_requests=get_all_leave_requests(),
                error_msg="Database error.",
            ),
            500,
        )
