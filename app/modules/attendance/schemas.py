"""
Pydantic schemas for Attendance API.
"""

from typing import Optional
from datetime import date, datetime
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field


class AttendanceStatus(str, Enum):
    """Enum for attendance status."""

    PRESENT = "Present"
    ABSENT = "Absent"


class AttendanceCreate(BaseModel):
    """Request model for creating an attendance record."""

    employee_id: UUID
    date: date
    status: AttendanceStatus


class AttendanceUpdate(BaseModel):
    """Request model for updating an attendance record."""

    status: AttendanceStatus


class AttendanceResponse(BaseModel):
    """Response model for attendance data."""

    id: UUID
    employee_id: UUID
    date: date
    status: AttendanceStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
