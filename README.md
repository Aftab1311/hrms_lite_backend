# HRMS Lite Backend

A production-ready REST API backend for a lightweight Human Resource Management System built with FastAPI, asyncpg, and PostgreSQL.

## Features

- **Employee Management**: Create, read, update, delete employee records
- **Attendance Tracking**: Log and manage daily attendance records
- **Reporting**: Generate attendance summaries and range-based reports
- **Async-first**: Built on FastAPI with async/await throughout
- **Connection Pooling**: Efficient database connection management with asyncpg
- **Error Handling**: Comprehensive global exception handling with consistent responses
- **Validation**: Pydantic v2 request/response validation
- **Environment Config**: 12-factor app pattern with pydantic-settings

## Tech Stack

- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn 0.24.0
- **Database Driver**: asyncpg 0.29.0
- **Database Queries**: databases 0.8.0 (async query builder)
- **Validation**: Pydantic 2.5.0
- **Configuration**: pydantic-settings 2.1.0
- **Python**: 3.11+

## Project Structure

```
app/
├── core/
│   ├── config.py           # Environment configuration (BaseSettings)
│   ├── database.py         # Database connection pool setup
│   └── __init__.py
├── modules/
│   ├── employees/          # Employee management API
│   │   ├── schemas.py      # Pydantic models
│   │   ├── service.py      # Business logic & database queries
│   │   ├── controller.py   # Request/response orchestration
│   │   ├── router.py       # API routes
│   │   └── __init__.py
│   ├── attendance/         # Attendance tracking API
│   │   ├── schemas.py
│   │   ├── service.py
│   │   ├── controller.py
│   │   ├── router.py
│   │   └── __init__.py
│   ├── reports/            # Reporting API
│   │   ├── schemas.py
│   │   ├── service.py
│   │   ├── router.py
│   │   └── __init__.py
│   └── __init__.py
├── middlewares/
│   ├── error_handler.py    # Global exception handlers
│   └── __init__.py
├── schemas.py              # Generic response wrappers
├── main.py                 # FastAPI app setup & lifespan
└── __init__.py
.env.example                # Environment variables template
requirements.txt            # Python dependencies (pinned versions)
hrms_lite_setup.sql         # PostgreSQL database schema
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Edit `.env`:
```
APP_PORT=8000
APP_HOST=0.0.0.0
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/hrms_lite
DB_MIN_POOL_SIZE=2
DB_MAX_POOL_SIZE=10
```

### 3. Initialize Database

```bash
psql -U postgres -d hrms_lite -f hrms_lite_setup.sql
```

### 4. Run the Server

```bash
python -m app.main
```

Server will be available at `http://localhost:8000`

## API Reference

### Health & Info

```
GET /health               - Health check endpoint
GET /                     - API overview
GET /docs                 - Interactive API documentation (Swagger UI)
GET /redoc                - ReDoc documentation
```

### Employee Management

```
GET    /api/employees              - List all employees (optional ?department= filter)
POST   /api/employees              - Create employee
GET    /api/employees/{id}         - Get single employee
PUT    /api/employees/{id}         - Update employee
DELETE /api/employees/{id}         - Delete employee
```

### Attendance Tracking

```
GET    /api/attendance             - List records (?employee_id=, ?date=, ?start_date=, ?end_date=, ?status=)
POST   /api/attendance             - Create record
GET    /api/attendance/{id}        - Get single record
PUT    /api/attendance/{id}        - Update status
DELETE /api/attendance/{id}        - Delete record
```

### Reporting

```
GET    /api/reports/attendance-summary      - Present/absent count per employee (optional ?department=)
GET    /api/reports/attendance-by-range     - Attendance by date range (required ?start_date=, ?end_date=)
```

## Response Format

All responses follow a consistent envelope format:

### Success Response (Single)
```json
{
  "success": true,
  "data": { ... }
}
```

### Success Response (List)
```json
{
  "success": true,
  "count": 10,
  "data": [ ... ]
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message here"
}
```

## Error Handling

- **400 Bad Request**: Invalid input data
- **404 Not Found**: Resource not found
- **409 Conflict**: Duplicate unique constraint (employee_id, email, employee+date)
- **422 Unprocessable Entity**: Validation error with field-level details
- **500 Internal Server Error**: Unhandled server exception

## Database Schema

### employees Table
- `id` (UUID) - Primary key
- `employee_id` (VARCHAR 20) - Unique human-readable code (e.g., EMP-001)
- `full_name` (VARCHAR 150) - Employee name
- `email` (VARCHAR 255) - Unique corporate email
- `department` (VARCHAR 100) - Department name
- `created_at` (TIMESTAMPTZ) - Created timestamp
- `updated_at` (TIMESTAMPTZ) - Auto-updated on modifications

### attendance Table
- `id` (UUID) - Primary key
- `employee_id` (UUID) - Foreign key → employees.id (CASCADE)
- `date` (DATE) - Attendance date
- `status` (ENUM) - 'Present' or 'Absent'
- `created_at` (TIMESTAMPTZ) - Created timestamp
- `updated_at` (TIMESTAMPTZ) - Auto-updated on modifications
- Unique constraint: (employee_id, date)

## Example Requests

### Create Employee
```bash
curl -X POST http://localhost:8000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP-001",
    "full_name": "John Doe",
    "email": "john@example.com",
    "department": "Engineering"
  }'
```

### Create Attendance
```bash
curl -X POST http://localhost:8000/api/attendance \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "550e8400-e29b-41d4-a716-446655440000",
    "date": "2026-02-27",
    "status": "Present"
  }'
```

### Get Attendance Summary
```bash
curl http://localhost:8000/api/reports/attendance-summary?department=Engineering
```

### Get Attendance by Date Range
```bash
curl "http://localhost:8000/api/reports/attendance-by-range?start_date=2026-02-01&end_date=2026-02-28"
```

## Database Connection Pool

The application uses the `databases` library with asyncpg for efficient async database queries:

- **Min Pool Size**: 2 (default, configurable)
- **Max Pool Size**: 10 (default, configurable)
- **Connection Reuse**: Automatic via SQLAlchemy-style context manager
- **Lifespan Management**: Integrated with FastAPI's lifespan context manager

## Development

### Running Tests (placeholder for test setup)

```bash
pytest
```

### Code Style

The codebase follows PEP 8 with type hints throughout.

## Production Deployment

For production, consider:

1. Use a production ASGI server (Gunicorn with uvicorn workers)
2. Enable CORS middleware if needed
3. Configure proper logging and monitoring
4. Use environment-specific .env files
5. Enable HTTPS/TLS
6. Set up database backups
7. Configure connection pool sizes based on workload
8. Add request rate limiting and authentication
9. Use a reverse proxy (Nginx)

Example production startup:
```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check DATABASE_URL format: `postgresql://user:password@host:port/database`
- Ensure database and user exist
- Test connection: `psql -U user -h localhost -d hrms_lite -c "SELECT 1"`

### Port Already in Use
Change APP_PORT in .env or pass custom port via environment variable

### Module Import Errors
Ensure PYTHONPATH includes the project root, or run with: `python -m app.main`

## License

[Your License Here]

## Contact

[Your Contact Information]
#   h r m s _ l i t e _ b a c k e n d  
 #   h r m s _ l i t e _ b a c k e n d  
 #   h r m s _ l i t e _ b a c k e n d  
 