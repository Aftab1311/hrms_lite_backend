"""
Pydantic schemas for Employee API.
"""

from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
import re


class EmployeeCreate(BaseModel):
    """Request model for creating an employee."""

    employee_id: str = Field(..., min_length=1, max_length=20)
    full_name: str = Field(..., min_length=1, max_length=150)
    email: str = Field(..., max_length=255)
    department: str = Field(..., min_length=1, max_length=100)

    @field_validator("employee_id")
    @classmethod
    def employee_id_not_empty(cls, v: str) -> str:
        """Ensure employee_id is not empty after trimming."""
        if not v.strip():
            raise ValueError("employee_id cannot be empty or whitespace")
        return v

    @field_validator("full_name")
    @classmethod
    def full_name_not_empty(cls, v: str) -> str:
        """Ensure full_name is not empty after trimming."""
        if not v.strip():
            raise ValueError("full_name cannot be empty or whitespace")
        return v

    @field_validator("email")
    @classmethod
    def email_format_valid(cls, v: str) -> str:
        """Validate email format using regex."""
        pattern = r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("department")
    @classmethod
    def department_not_empty(cls, v: str) -> str:
        """Ensure department is not empty after trimming."""
        if not v.strip():
            raise ValueError("department cannot be empty or whitespace")
        return v


class EmployeeUpdate(BaseModel):
    """Request model for updating an employee (all fields optional)."""

    employee_id: Optional[str] = Field(None, min_length=1, max_length=20)
    full_name: Optional[str] = Field(None, min_length=1, max_length=150)
    email: Optional[str] = Field(None, max_length=255)
    department: Optional[str] = Field(None, min_length=1, max_length=100)

    @field_validator("employee_id")
    @classmethod
    def employee_id_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure employee_id is not empty after trimming if provided."""
        if v is not None and not v.strip():
            raise ValueError("employee_id cannot be empty or whitespace")
        return v

    @field_validator("full_name")
    @classmethod
    def full_name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure full_name is not empty after trimming if provided."""
        if v is not None and not v.strip():
            raise ValueError("full_name cannot be empty or whitespace")
        return v

    @field_validator("email")
    @classmethod
    def email_format_valid(cls, v: Optional[str]) -> Optional[str]:
        """Validate email format using regex if provided."""
        if v is not None:
            pattern = r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$"
            if not re.match(pattern, v):
                raise ValueError("Invalid email format")
        return v

    @field_validator("department")
    @classmethod
    def department_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure department is not empty after trimming if provided."""
        if v is not None and not v.strip():
            raise ValueError("department cannot be empty or whitespace")
        return v


class EmployeeResponse(BaseModel):
    """Response model for employee data."""

    id: UUID
    employee_id: str
    full_name: str
    email: str
    department: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
