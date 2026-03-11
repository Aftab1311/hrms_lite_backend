"""
Global exception handler middleware for consistent error responses.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from app.schemas import ErrorResponse


logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers on the FastAPI app.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(error=exc.detail).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handle Pydantic validation errors with field-level details."""
        errors = []
        for error in exc.errors():
            field = ".".join(str(x) for x in error["loc"][1:])
            message = error["msg"]
            errors.append(f"{field}: {message}")

        error_detail = "; ".join(errors) if errors else "Validation error"
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(error=error_detail).model_dump(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(error="Internal server error").model_dump(),
        )
