"""
Generic response wrapper types for consistent API responses.
"""

from typing import Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Generic success response wrapper."""

    success: bool = True
    data: T


class ListResponse(BaseModel, Generic[T]):
    """Generic list response wrapper with count."""

    success: bool = True
    count: int
    data: List[T]


class ErrorResponse(BaseModel):
    """Standard error response wrapper."""

    success: bool = False
    error: str
