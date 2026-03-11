"""
Pydantic schemas for Reporting API.
"""

from typing import Optional
from uuid import UUID
from datetime import date
from pydantic import BaseModel


class AttendanceSummaryItem(BaseModel):
    """Response model for attendance summary per employee."""

    employee_id: UUID
    full_name: str
    total_present: int
    total_absent: int


class AttendanceByRangeItem(BaseModel):
    """Response model for attendance by date range."""

    full_name: str
    date: date
    status: str
