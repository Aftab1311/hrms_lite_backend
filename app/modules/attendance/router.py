"""
API Route Handlers for Employee Attendance Operations.
"""

from typing import Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from databases import Database

from app.core.database import db_connector
from app.schemas import SuccessResponse, ListResponse
from app.modules.attendance.schemas import (
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse,
)
from app.modules.attendance.service import AttendanceService
from app.modules.attendance.controller import AttendanceController

# Set up the API router for attendance logging
router = APIRouter(prefix="/api/attendance", tags=["Attendance"])

async def resolve_attendance_controller() -> AttendanceController:
    """Build and inject the Attendance Controller instance."""
    svc = AttendanceService(db_connector.database)
    return AttendanceController(svc)

@router.get(
    "",
    response_model=ListResponse[AttendanceResponse],
    summary="Browse recorded attendance",
    status_code=status.HTTP_200_OK
)
async def browse_attendance_records(
    employee_id: Optional[UUID] = Query(None, description="Target a specific employee's UUID"),
    date: Optional[date] = Query(None, description="Exact date to look up"),
    start_date: Optional[date] = Query(None, description="Begin boundary of date range"),
    end_date: Optional[date] = Query(None, description="End boundary of date range"),
    status_val: Optional[str] = Query(None, alias="status", description="Filter by presence 'Present' or 'Absent'"),
    att_ctrl: AttendanceController = Depends(resolve_attendance_controller),
) -> ListResponse[AttendanceResponse]:
    """
    Scan through attendance logs matching the provided optional filtering criteria.
    """
    fetched_logs = await att_ctrl.list_attendance(
        employee_id=employee_id,
        date_filter=date,
        start_date=start_date,
        end_date=end_date,
        status=status_val,
    )
    
    return ListResponse(
        count=len(fetched_logs), 
        data=fetched_logs
    )

@router.post(
    "",
    response_model=SuccessResponse[AttendanceResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Log daily attendance"
)
async def log_daily_attendance(
    attendance_payload: AttendanceCreate,
    att_ctrl: AttendanceController = Depends(resolve_attendance_controller),
) -> SuccessResponse[AttendanceResponse]:
    """
    Submits a new attendance ping into the system for a given employee and day.
    """
    inserted_log = await att_ctrl.create_attendance(attendance_payload)
    return SuccessResponse(data=inserted_log)

@router.get(
    "/{attendance_id}",
    response_model=SuccessResponse[AttendanceResponse],
    summary="Fetch a specific attendance log details",
    status_code=status.HTTP_200_OK
)
async def fetch_single_attendance_entry(
    attendance_id: UUID,
    att_ctrl: AttendanceController = Depends(resolve_attendance_controller),
) -> SuccessResponse[AttendanceResponse]:
    """
    Retrieve exactly one attendance ledger record by its strictly unique identifier.
    """
    found_record = await att_ctrl.get_attendance(attendance_id)
    return SuccessResponse(data=found_record)

@router.put(
    "/{attendance_id}",
    response_model=SuccessResponse[AttendanceResponse],
    summary="Adjust an existing attendance status",
    status_code=status.HTTP_200_OK
)
async def adjust_attendance_record(
    attendance_id: UUID,
    attendance_payload: AttendanceUpdate,
    att_ctrl: AttendanceController = Depends(resolve_attendance_controller),
) -> SuccessResponse[AttendanceResponse]:
    """
    Make corrections to a submitted attendance log (typically to fix status strings).
    """
    updated_record = await att_ctrl.update_attendance(attendance_id, attendance_payload)
    return SuccessResponse(data=updated_record)

@router.delete(
    "/{attendance_id}", 
    status_code=status.HTTP_204_NO_CONTENT, 
    summary="Erase an attendance record completely"
)
async def drop_attendance_entry(
    attendance_id: UUID,
    att_ctrl: AttendanceController = Depends(resolve_attendance_controller),
) -> None:
    """
    Permanently strike an attendance record from the database.
    """
    await att_ctrl.delete_attendance(attendance_id)
