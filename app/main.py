"""
FastAPI application setup with router registration and lifespan management.
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import db_connector
from app.middlewares.error_handler import register_exception_handlers
from app.modules.employees.router import router as employees_router
from app.modules.attendance.router import router as attendance_router
from app.modules.reports.router import router as reports_router


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for startup/shutdown events.
    Manages database connection pool lifecycle.
    """
    # Startup
    logger.info("Starting HRMS Lite API...")
    await db_connector.connect()
    logger.info("Database connection pool established")

    yield

    # Shutdown
    logger.info("Shutting down HRMS Lite API...")
    await db_connector.disconnect()
    logger.info("Database connection pool closed")


# Create FastAPI app with lifespan
app = FastAPI(
    title="HRMS Lite API",
    description="Lightweight Human Resource Management System REST API",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register global exception handlers
register_exception_handlers(app)

# Register routers
app.include_router(employees_router)
app.include_router(attendance_router)
app.include_router(reports_router)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status with UTC timestamp
    """
    return JSONResponse(
        content={
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    )


@app.get("/")
async def root():
    """
    Root endpoint providing API information.

    Returns:
        API overview and available endpoints
    """
    return JSONResponse(
        content={
            "name": "HRMS Lite API",
            "version": "1.0.0",
            "description": "Lightweight Human Resource Management System",
            "endpoints": {
                "health": "/health",
                "employees": "/api/employees",
                "attendance": "/api/attendance",
                "reports": "/api/reports",
                "docs": "/docs",
            },
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=False,
    )
