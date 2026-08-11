from datetime import datetime, timezone
from app import db


class LeaveRequest(db.Model):
    """
    Model representing an employee leave request.
    """

    __tablename__ = "leave_requests"

    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="PENDING")
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    @property
    def duration_days(self) -> int:
        """
        Calculates calendar days for the leave duration.
        Includes both start_date and end_date.
        """
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    def to_dict(self):
        return {
            "id": self.id,
            "employee_name": self.employee_name,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "reason": self.reason,
            "status": self.status,
            "duration_days": self.duration_days,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<LeaveRequest id={self.id} employee='{self.employee_name}' status='{self.status}'>"
