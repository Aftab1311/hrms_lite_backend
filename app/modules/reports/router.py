"""
Endpoints for generating and retrieving employee reports.
"""

from typing import Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, Query, status

from app.core.database import db_connector
from app.schemas import ListResponse
from app.modules.reports.schemas import AttendanceSummaryItem, AttendanceByRangeItem
from app.modules.reports.service import ReportService

# Initialize the router instance
router = APIRouter(prefix="/api/reports", tags=["Reports"])

async def build_report_service() -> ReportService:
    """Instantiate and provide the reporting service."""
    return ReportService(db_connector.database)

@router.get(
    "/attendance-summary",
    response_model=ListResponse[AttendanceSummaryItem],
    summary="Employee attendance statistics",
    status_code=status.HTTP_200_OK
)
async def fetch_department_or_global_summary(
    department: Optional[str] = Query(None, description="Filter by a specific department"),
    reporting_svc: ReportService = Depends(build_report_service),
) -> ListResponse[AttendanceSummaryItem]:
    """
    Retrieve summarized attendance stats (present vs absent days) per employee.
    """
    raw_stats = await reporting_svc.attendance_summary(department=department)
    
    formatted_results = []
    for stat_row in raw_stats:
        formatted_results.append(AttendanceSummaryItem(**stat_row))
        
    return ListResponse(
        count=len(formatted_results),
        data=formatted_results
    )

@router.get(
    "/attendance-by-range",
    response_model=ListResponse[AttendanceByRangeItem],
    summary="Detailed periodic attendance logs",
    status_code=status.HTTP_200_OK
)
async def fetch_periodic_attendance_logs(
    start_date: date = Query(..., description="Beginning of the reporting period (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End of the reporting period (YYYY-MM-DD)"),
    employee_id: Optional[UUID] = Query(None, description="Specific employee to filter by"),
    department: Optional[str] = Query(None, description="Department filter"),
    reporting_svc: ReportService = Depends(build_report_service),
) -> ListResponse[AttendanceByRangeItem]:
    """
    Retrieve attendance logs for all or specific employees within a given timeframe.
    """
    target_emp_id = str(employee_id) if employee_id else None
    
    fetched_records = await reporting_svc.attendance_by_range(
        start_date=start_date,
        end_date=end_date,
        employee_id=target_emp_id,
        department=department,
    )
    
    parsed_items = [
        AttendanceByRangeItem(**entry)
        for entry in fetched_records
    ]
    
    return ListResponse(
        count=len(parsed_items), 
        data=parsed_items
    )
