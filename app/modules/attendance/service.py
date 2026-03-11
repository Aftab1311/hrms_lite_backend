"""
Service layer for Attendance operations.
All database queries are performed here using the databases library.
"""

from typing import Optional, List
from uuid import UUID
from datetime import date
import asyncpg
from databases import Database

from app.modules.attendance.schemas import (
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse,
    AttendanceStatus,
)


class AttendanceService:
    """Service for attendance-related database operations."""

    def __init__(self, database: Database):
        """
        Initialize with database connection.

        Args:
            database: Connected databases.Database instance
        """
        self.db = database

    async def list_attendance(
        self,
        employee_id: Optional[UUID] = None,
        date_filter: Optional[date] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[AttendanceStatus] = None,
    ) -> List[dict]:
        """
        Retrieve attendance records with optional filters.

        Args:
            employee_id: Filter by employee UUID
            date_filter: Filter by specific date
            start_date: Filter by date range start
            end_date: Filter by date range end
            status: Filter by status (Present/Absent)

        Returns:
            List of attendance dictionaries
        """
        conditions = []
        params = {}

        if employee_id:
            conditions.append("employee_id = :employee_id")
            params["employee_id"] = str(employee_id)

        if date_filter:
            conditions.append("date = :date_filter")
            params["date_filter"] = date_filter

        if start_date:
            conditions.append("date >= :start_date")
            params["start_date"] = start_date

        if end_date:
            conditions.append("date <= :end_date")
            params["end_date"] = end_date

        if status:
            conditions.append("status = :status")
            params["status"] = status.value

        where_clause = " AND ".join(conditions)
        if where_clause:
            where_clause = f"WHERE {where_clause}"

        query = f"""
            SELECT id, employee_id, date, status, created_at, updated_at
            FROM attendance
            {where_clause}
            ORDER BY date DESC, employee_id
        """

        return await self.db.fetch_all(query, params)

    async def get_attendance_by_id(self, attendance_id: UUID) -> Optional[dict]:
        """
        Retrieve a single attendance record by UUID.

        Args:
            attendance_id: UUID of the attendance record

        Returns:
            Attendance dictionary or None if not found
        """
        query = """
            SELECT id, employee_id, date, status, created_at, updated_at
            FROM attendance
            WHERE id = :id
        """
        return await self.db.fetch_one(query, {"id": str(attendance_id)})

    async def create_attendance(self, attendance_data: AttendanceCreate) -> dict:
        """
        Create a new attendance record.

        Args:
            attendance_data: AttendanceCreate request model

        Raises:
            ValueError: If duplicate (employee_id, date) combination

        Returns:
            Created attendance dictionary
        """
        query = """
            INSERT INTO attendance (employee_id, date, status)
            VALUES (:employee_id, :date, :status)
            RETURNING id, employee_id, date, status, created_at, updated_at
        """
        try:
            return await self.db.fetch_one(
                query,
                {
                    "employee_id": str(attendance_data.employee_id),
                    "date": attendance_data.date,
                    "status": attendance_data.status.value,
                },
            )
        except asyncpg.UniqueViolationError as e:
            raise ValueError(
                f"Duplicate: Attendance already exists for this employee on this date"
            ) from e
        except asyncpg.ForeignKeyViolationError as e:
            raise ValueError(f"Foreign key error: Employee not found") from e

    async def update_attendance(
        self, attendance_id: UUID, attendance_data: AttendanceUpdate
    ) -> Optional[dict]:
        """
        Update an attendance record (status only).

        Args:
            attendance_id: UUID of the attendance record to update
            attendance_data: AttendanceUpdate request model

        Raises:
            ValueError: If record not found

        Returns:
            Updated attendance dictionary
        """
        # Check if record exists
        existing = await self.get_attendance_by_id(attendance_id)
        if not existing:
            raise ValueError("Attendance record not found")

        query = """
            UPDATE attendance
            SET status = :status
            WHERE id = :id
            RETURNING id, employee_id, date, status, created_at, updated_at
        """

        return await self.db.fetch_one(
            query,
            {
                "id": str(attendance_id),
                "status": attendance_data.status.value,
            },
        )

    async def delete_attendance(self, attendance_id: UUID) -> bool:
        """
        Delete an attendance record.

        Args:
            attendance_id: UUID of the attendance record to delete

        Returns:
            True if deleted, False if not found
        """
        query = "DELETE FROM attendance WHERE id = :id"
        result = await self.db.execute(query, {"id": str(attendance_id)})
        return result > 0
