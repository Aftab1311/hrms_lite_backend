"""
Controller layer for Attendance API.
Interprets validation logic and links routers to the DB service.
"""

from typing import Optional
from uuid import UUID
from datetime import date
from fastapi import HTTPException

from app.modules.attendance.schemas import (
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse,
    AttendanceStatus,
)
from app.modules.attendance.service import AttendanceService


class AttendanceController:
    """Main business logic proxy for attendance logs."""

    def __init__(self, service: AttendanceService):
        self.service = service

    async def list_attendance(
        self,
        employee_id: Optional[UUID] = None,
        date_filter: Optional[date] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
    ) -> list[AttendanceResponse]:
        """
        Fetch any recorded attendance entries matching the provided boundaries and statuses.
        """
        status_enum = None
        if status:
            try:
                status_enum = AttendanceStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid attendance status. We only support 'Present' or 'Absent'."
                )

        raw_logs = await self.service.list_attendance(
            employee_id=employee_id,
            date_filter=date_filter,
            start_date=start_date,
            end_date=end_date,
            status=status_enum,
        )
        
        return [AttendanceResponse(**row) for row in raw_logs]

    async def get_attendance(self, attendance_id: UUID) -> AttendanceResponse:
        """
        Retrieve a single log entry. Flings a 404 if the given ID doesn't exist.
        """
        found_entry = await self.service.get_attendance_by_id(attendance_id)
        
        if not found_entry:
            raise HTTPException(status_code=404, detail="We couldn't locate that attendance record")
            
        return AttendanceResponse(**found_entry)

    async def create_attendance(self, data: AttendanceCreate) -> AttendanceResponse:
        """
        Creates a new daily log. Will catch duplicate logs or invalid employee references and
        transform them to the correct HTTP status codes natively.
        """
        try:
            new_log = await self.service.create_attendance(data)
            return AttendanceResponse(**new_log)
        except ValueError as err:
            err_msg = str(err)
            
            if "Duplicate" in err_msg:
                raise HTTPException(
                    status_code=409,
                    detail="An attendance log already exists for this person on this exact date"
                )
            elif "Foreign key" in err_msg:
                raise HTTPException(status_code=400, detail="The specified employee does not exist")
                
            raise HTTPException(status_code=400, detail=err_msg)

    async def update_attendance(
        self, attendance_id: UUID, data: AttendanceUpdate
    ) -> AttendanceResponse:
        """
        Patches an existing entry (usually simply to swap between Present/Absent).
        """
        try:
            patched_entry = await self.service.update_attendance(attendance_id, data)
            return AttendanceResponse(**patched_entry)
        except ValueError as err:
            err_msg = str(err)
            if "not found" in err_msg.lower():
                raise HTTPException(status_code=404, detail=err_msg)
            raise HTTPException(status_code=400, detail=err_msg)

    async def delete_attendance(self, attendance_id: UUID) -> bool:
        """
        Blows away an attendance record from the database.
        """
        was_deleted = await self.service.delete_attendance(attendance_id)
        
        if not was_deleted:
            raise HTTPException(status_code=404, detail="Can't delete this log as it was not found")
            
        return True
