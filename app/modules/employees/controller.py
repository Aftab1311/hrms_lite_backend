"""
Controller layer for Employee API.
Orchestrates request validation and delegates database operations to the service layer.
"""

from typing import Optional
from uuid import UUID
from fastapi import HTTPException

from app.modules.employees.schemas import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
)
from app.modules.employees.service import EmployeeService


class EmployeeController:
    """Central logic hub for employee endpoints."""

    def __init__(self, service: EmployeeService):
        self.service = service

    async def list_employees(
        self, department: Optional[str] = None
    ) -> list[EmployeeResponse]:
        """
        Fetch and serialize a list of employees. 
        If a department is passed, the results will be restricted to that department.
        """
        fetched_rows = await self.service.list_employees(department=department)
        return [EmployeeResponse(**row) for row in fetched_rows]

    async def get_employee(self, employee_id: UUID) -> EmployeeResponse:
        """
        Look up a single employee by their UUID. Throws a 404 if they cannot be found.
        """
        target_employee = await self.service.get_employee_by_id(employee_id)
        
        if not target_employee:
            raise HTTPException(status_code=404, detail="Requested employee does not exist")
            
        return EmployeeResponse(**target_employee)

    async def create_employee(self, data: EmployeeCreate) -> EmployeeResponse:
        """
        Handle the creation logic for a new staff member, capturing any duplicate entry errors 
        and mapping them to a 409 Conflict.
        """
        try:
            persisted_employee = await self.service.create_employee(data)
            return EmployeeResponse(**persisted_employee)
        except ValueError as err:
            err_msg = str(err)
            if "Duplicate" in err_msg:
                raise HTTPException(
                    status_code=409,
                    detail="Employee ID or email is already registered in the system"
                )
            raise HTTPException(status_code=400, detail=err_msg)

    async def update_employee(
        self, employee_id: UUID, data: EmployeeUpdate
    ) -> EmployeeResponse:
        """
        Apply a partial update to an employee's profile. Maps missing records to 404
        and duplicate conflicts to 409.
        """
        try:
            updated_state = await self.service.update_employee(employee_id, data)
            return EmployeeResponse(**updated_state)
        except ValueError as err:
            err_msg = str(err)
            
            if "not found" in err_msg.lower():
                raise HTTPException(status_code=404, detail=err_msg)
            elif "Duplicate" in err_msg:
                raise HTTPException(status_code=409, detail="Provided Employee ID or email conflicts with an existing one")
                
            raise HTTPException(status_code=400, detail=err_msg)

    async def delete_employee(self, employee_id: UUID) -> bool:
        """
        Permanently purge an employee and return True upon success. Throws 404 if missing.
        """
        was_removed = await self.service.delete_employee(employee_id)
        
        if not was_removed:
            raise HTTPException(status_code=404, detail="Cannot delete: Employee not found")
            
        return True
