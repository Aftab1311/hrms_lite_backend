"""
Service layer for Reporting operations.
Executes raw SQL queries against the database to generate attendance insights.
"""

from typing import Optional, List
from datetime import date
from databases import Database

from app.modules.reports.schemas import (
    AttendanceSummaryItem,
    AttendanceByRangeItem,
)


class ReportService:
    """Manages all database interactions required for report generation."""

    def __init__(self, database: Database):
        self.db = database

    async def attendance_summary(
        self, department: Optional[str] = None
    ) -> List[dict]:
        """
        Aggregate total present and absent counts for each employee.
        Can be scoped to a specific department if provided.
        """
        if department:
            sql = """
                SELECT e.id AS employee_id, e.full_name,
                       COUNT(*) FILTER (WHERE a.status = 'Present') AS total_present,
                       COUNT(*) FILTER (WHERE a.status = 'Absent')  AS total_absent
                FROM employees e
                LEFT JOIN attendance a ON a.employee_id = e.id
                WHERE e.department = :department
                GROUP BY e.id, e.full_name
                ORDER BY e.full_name
            """
            return await self.db.fetch_all(sql, {"department": department})
        
        sql = """
            SELECT e.id AS employee_id, e.full_name,
                   COUNT(*) FILTER (WHERE a.status = 'Present') AS total_present,
                   COUNT(*) FILTER (WHERE a.status = 'Absent')  AS total_absent
            FROM employees e
            LEFT JOIN attendance a ON a.employee_id = e.id
            GROUP BY e.id, e.full_name
            ORDER BY e.full_name
        """
        return await self.db.fetch_all(sql)

    async def attendance_by_range(
        self,
        start_date: date,
        end_date: date,
        employee_id: Optional[str] = None,
        department: Optional[str] = None,
    ) -> List[dict]:
        """
        Retrieve a detailed chronological log of attendance for a given time window.
        Supports optional filtering by specific employee or entire departments.
        """
        clause_list = [
            "a.date BETWEEN :start_date AND :end_date"
        ]
        query_args = {
            "start_date": start_date,
            "end_date": end_date,
        }

        if employee_id:
            clause_list.append("a.employee_id = :employee_id")
            query_args["employee_id"] = employee_id

        if department:
            clause_list.append("e.department = :department")
            query_args["department"] = department

        filters_sql = " AND ".join(clause_list)

        sql = f"""
            SELECT e.full_name, a.date, a.status
            FROM attendance a
            JOIN employees e ON e.id = a.employee_id
            WHERE {filters_sql}
            ORDER BY a.date, e.full_name
        """

        return await self.db.fetch_all(sql, query_args)
