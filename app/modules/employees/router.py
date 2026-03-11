"""
API Router handling all operations related to employee management.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from databases import Database

from app.core.database import db_connector
from app.schemas import SuccessResponse, ListResponse
from app.modules.employees.schemas import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.modules.employees.service import EmployeeService
from app.modules.employees.controller import EmployeeController

# Initialize the router block for employees
router = APIRouter(prefix="/api/employees", tags=["Employee"])

async def build_employee_controller() -> EmployeeController:
    """Instantiate the Employee Controller with injected dependencies."""
    svc = EmployeeService(db_connector.database)
    return EmployeeController(svc)

@router.get(
    "",
    response_model=ListResponse[EmployeeResponse],
    summary="Fetch the company employee directory",
    status_code=status.HTTP_200_OK
)
async def fetch_employee_directory(
    department: Optional[str] = Query(None, description="Filter output by department name"),
    emp_ctrl: EmployeeController = Depends(build_employee_controller),
) -> ListResponse[EmployeeResponse]:
    """
    Retrieve a comprehensive list of all employees in the system, optionally filtered by department.
    """
    fetched_staff = await emp_ctrl.list_employees(department=department)
    
    return ListResponse(
        count=len(fetched_staff), 
        data=fetched_staff
    )

@router.post(
    "",
    response_model=SuccessResponse[EmployeeResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Onboard a new employee"
)
async def onboard_new_employee(
    payload: EmployeeCreate,
    emp_ctrl: EmployeeController = Depends(build_employee_controller),
) -> SuccessResponse[EmployeeResponse]:
    """
    Register a newly hired employee into the database.
    """
    new_hire = await emp_ctrl.create_employee(payload)
    return SuccessResponse(data=new_hire)

@router.get(
    "/{employee_id}",
    response_model=SuccessResponse[EmployeeResponse],
    summary="Retrieve specific employee details",
    status_code=status.HTTP_200_OK
)
async def retrieve_employee_details(
    employee_id: UUID,
    emp_ctrl: EmployeeController = Depends(build_employee_controller),
) -> SuccessResponse[EmployeeResponse]:
    """
    Look up detailed profile information for a specific staff member using their UUID.
    """
    profile = await emp_ctrl.get_employee(employee_id)
    return SuccessResponse(data=profile)

@router.put(
    "/{employee_id}",
    response_model=SuccessResponse[EmployeeResponse],
    summary="Modify existing employee record",
    status_code=status.HTTP_200_OK
)
async def modify_employee_record(
    employee_id: UUID,
    payload: EmployeeUpdate,
    emp_ctrl: EmployeeController = Depends(build_employee_controller),
) -> SuccessResponse[EmployeeResponse]:
    """
    Apply selective updates to an employee's profile information.
    """
    updated_profile = await emp_ctrl.update_employee(employee_id, payload)
    return SuccessResponse(data=updated_profile)

@router.delete(
    "/{employee_id}", 
    status_code=status.HTTP_204_NO_CONTENT, 
    summary="Remove an employee from the system"
)
async def remove_employee_entry(
    employee_id: UUID,
    emp_ctrl: EmployeeController = Depends(build_employee_controller),
) -> None:
    """
    Permanently delete an employee record. Note: This action will cascade to related attendance data.
    """
    await emp_ctrl.delete_employee(employee_id)
