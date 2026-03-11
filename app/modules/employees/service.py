"""
Service layer for Employee operations.
All database queries are performed here using the databases library.
"""

from typing import Optional, List
from uuid import UUID
import asyncpg
from databases import Database

from app.modules.employees.schemas import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
)


class EmployeeService:
    """Service for employee-related database operations."""

    def __init__(self, database: Database):
        """
        Initialize with database connection.

        Args:
            database: Connected databases.Database instance
        """
        self.db = database

    async def list_employees(
        self, department: Optional[str] = None
    ) -> List[dict]:
        """
        Retrieve all employees, optionally filtered by department.

        Args:
            department: Optional department name to filter by

        Returns:
            List of employee dictionaries
        """
        if department:
            query = """
                SELECT id, employee_id, full_name, email, department, created_at, updated_at
                FROM employees
                WHERE department = :department
                ORDER BY full_name
            """
            return await self.db.fetch_all(query, {"department": department})
        else:
            query = """
                SELECT id, employee_id, full_name, email, department, created_at, updated_at
                FROM employees
                ORDER BY full_name
            """
            return await self.db.fetch_all(query)

    async def get_employee_by_id(self, employee_id: UUID) -> Optional[dict]:
        """
        Retrieve a single employee by UUID.

        Args:
            employee_id: UUID of the employee

        Returns:
            Employee dictionary or None if not found
        """
        query = """
            SELECT id, employee_id, full_name, email, department, created_at, updated_at
            FROM employees
            WHERE id = :id
        """
        return await self.db.fetch_one(query, {"id": str(employee_id)})

    async def create_employee(self, employee_data: EmployeeCreate) -> dict:
        """
        Create a new employee.

        Args:
            employee_data: EmployeeCreate request model

        Raises:
            HTTPException: 409 if employee_id or email already exists

        Returns:
            Created employee dictionary
        """
        query = """
            INSERT INTO employees (employee_id, full_name, email, department)
            VALUES (:employee_id, :full_name, :email, :department)
            RETURNING id, employee_id, full_name, email, department, created_at, updated_at
        """
        try:
            return await self.db.fetch_one(
                query,
                {
                    "employee_id": employee_data.employee_id,
                    "full_name": employee_data.full_name,
                    "email": employee_data.email,
                    "department": employee_data.department,
                },
            )
        except asyncpg.UniqueViolationError as e:
            raise ValueError(
                f"Duplicate: {str(e)}"
            ) from e

    async def update_employee(
        self, employee_id: UUID, employee_data: EmployeeUpdate
    ) -> Optional[dict]:
        """
        Update an employee with partial data.

        Args:
            employee_id: UUID of the employee to update
            employee_data: EmployeeUpdate request model with optional fields

        Raises:
            ValueError: If record not found or duplicate field

        Returns:
            Updated employee dictionary
        """
        # Check if employee exists
        existing = await self.get_employee_by_id(employee_id)
        if not existing:
            raise ValueError("Employee not found")

        # Build dynamic update query with only non-None fields
        update_fields = []
        params = {"id": str(employee_id)}
        param_index = 1

        if employee_data.employee_id is not None:
            update_fields.append(f"employee_id = :param{param_index}")
            params[f"param{param_index}"] = employee_data.employee_id
            param_index += 1

        if employee_data.full_name is not None:
            update_fields.append(f"full_name = :param{param_index}")
            params[f"param{param_index}"] = employee_data.full_name
            param_index += 1

        if employee_data.email is not None:
            update_fields.append(f"email = :param{param_index}")
            params[f"param{param_index}"] = employee_data.email
            param_index += 1

        if employee_data.department is not None:
            update_fields.append(f"department = :param{param_index}")
            params[f"param{param_index}"] = employee_data.department
            param_index += 1

        # If no fields to update, return existing record
        if not update_fields:
            return existing

        query = f"""
            UPDATE employees
            SET {', '.join(update_fields)}
            WHERE id = :id
            RETURNING id, employee_id, full_name, email, department, created_at, updated_at
        """

        try:
            return await self.db.fetch_one(query, params)
        except asyncpg.UniqueViolationError as e:
            raise ValueError(
                f"Duplicate: {str(e)}"
            ) from e

    async def delete_employee(self, employee_id: UUID) -> bool:
        """
        Delete an employee (cascades to attendance records).

        Args:
            employee_id: UUID of the employee to delete

        Returns:
            True if deleted, False if not found
        """
        query = "DELETE FROM employees WHERE id = :id"
        result = await self.db.execute(query, {"id": str(employee_id)})
        return result > 0
