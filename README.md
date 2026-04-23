# AI Financial Management & ROI Intelligence Platform — Backend

A FastAPI backend for real-time financial intelligence, ROI tracking, employee value scoring, and AI-powered forecasting.

## Tech Stack

- **Framework:** FastAPI (Python 3.12)
- **Database:** PostgreSQL + SQLAlchemy (async) + asyncpg
- **Migrations:** Alembic
- **Auth:** JWT (python-jose) + bcrypt (passlib) + OAuth2 password flow
- **Validation:** Pydantic v2
- **Logging:** structlog (structured JSON)

## Project Structure

```
backend/
├── main.py                  # FastAPI app entry point
├── config.py                # Pydantic settings (reads .env)
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container build
├── alembic.ini              # Alembic config
├── migrations/              # Alembic migrations
│   ├── env.py
│   └── versions/
├── app/
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── base.py          # Base, TimestampMixin, IntegerPrimaryKeyMixin
│   │   ├── user.py          # User model + RoleEnum ✅
│   │   ├── project.py       # Project model + Relationships ✅
│   │   ├── expense.py       # Expense tracking model ✅
│   │   ├── employee.py      # Employee profile + skills ✅
│   │   ├── work_log.py      # Task & hours logging ✅
│   │   ├── alert.py         # System alerts & notifications ✅
│   │   ├── ai_prediction.py # ML prediction results ✅
│   │   └── project_assignment.py  # Staffing & assignments ✅
│   ├── schemas/             # Pydantic request/response models
│   │   ├── auth.py          # UserCreate, UserRead, TokenResponse ✅
│   │   ├── common.py        # PaginatedResponse, ErrorResponse ✅
│   │   └── ...              # Domain schemas (Project, Expense, etc.) ✅
│   ├── repositories/        # Data access layer (async CRUD)
│   │   ├── base_repo.py     # Generic BaseRepo[T] ✅
│   │   ├── user_repo.py     # UserRepo ✅
│   │   └── ...              # Domain repositories ✅
│   ├── services/            # Business logic layer
│   │   ├── auth_service.py  # Register, login, refresh ✅
│   │   └── ...              # Domain services (ROI calc, etc.) ✅
│   ├── api/                 # API routes
│   │   ├── deps.py          # Shared deps (get_db, get_current_user) ✅
│   │   └── v1/
│   │       ├── router.py    # Master router ✅
│   │       ├── auth.py      # Auth endpoints ✅
│   │       └── ...          # Domain routers (projects, expenses, ai, etc.) ✅
│   ├── core/                # Security, logging, exceptions
│   │   ├── security.py      # JWT + bcrypt ✅
│   │   ├── permissions.py   # RBAC require_role() ✅
│   │   ├── exceptions.py    # Custom exceptions + handlers ✅
│   │   ├── events.py        # Startup/shutdown lifespan ✅
│   │   └── logging.py       # Structured logging + TraceIDMiddleware ✅
│   ├── utils/               # Helpers (roi_calculator, pagination, etc.)
│   ├── background/          # Scheduled workers (anomaly scanner, alert checker)
│   └── db/
│       ├── session.py       # Async engine + session factory ✅
│       └── init_db.py       # Table creation + admin seeding ✅
└── tests/
    ├── unit/
    ├── integration/
    └── ai/
```

> ✅ = Implemented | TODO = Placeholder stub for you to implement

## Quick Start

### 1. Prerequisites

- **Python 3.12+**
- **PostgreSQL** running on `localhost:5432`
- Create a database (e.g. `financial_ri`)

### 2. Clone & Install

```bash
cd backend
python -m venv roi_env
roi_env\Scripts\activate        # Windows
# source roi_env/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

### 3. Configure Environment

Copy the example env file and fill in your values:

```bash
copy .env.example .env          # Windows
# cp .env.example .env          # macOS/Linux
```

Edit `.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/financial_ri
JWT_SECRET_KEY=your-secret-key-here
JWT_EXPIRE_MINUTES=30
JWT_REFRESH_EXPIRE_MINUTES=10080
ENVIRONMENT=dev
```

### 4. Run Migrations

```bash
alembic upgrade head
```

### 5. Start the Server

```bash
uvicorn main:app --reload
```

The server starts at **http://127.0.0.1:8000**

- **Swagger UI:** http://127.0.0.1:8000/docs
- **Health check:** http://127.0.0.1:8000/health

### 6. Default Admin Account

On first startup, `init_db.py` seeds a default admin user:

| Field    | Value                       |
|----------|-----------------------------|
| Email    | `admin@financial-roi.com`   |
| Password | `admin123`                  |
| Role     | `admin`                     |

> ⚠️ Change the admin password in production!

## Architecture

This project follows a **4-layer architecture**:

```
Routes (API) → Services (business logic) → Repositories (data access) → Models (ORM)
```

## Authentication & RBAC

### Auth Flow
1. `POST /api/v1/auth/register` — Create a new user
2. `POST /api/v1/auth/login` — Get JWT access + refresh tokens
3. `GET /api/v1/auth/me` — Get current user profile (requires Bearer token)
4. `POST /api/v1/auth/refresh` — Refresh an expired access token

### Roles (RBAC)

| Role              | Description                         |
|-------------------|-------------------------------------|
| `admin`           | Full access to all endpoints        |
| `finance_manager` | Financial data, expenses, reports   |
| `project_manager` | Projects, employees, work logs      |
| `employee`        | Own data, submit work logs          |

Use `require_role()` dependency to protect endpoints:
```python
from app.core.permissions import require_role, RoleEnum

@router.get("/admin-only", dependencies=[Depends(require_role(RoleEnum.admin))])
async def admin_endpoint():
    ...
```

## For New Developers

Files marked as **TODO** contain docstrings explaining what to implement. Follow the patterns established in the auth flow:

1. **Model** → Define your SQLAlchemy ORM model in `app/models/`
2. **Schema** → Create Pydantic request/response schemas in `app/schemas/`
3. **Repository** → Extend `BaseRepo` for data access in `app/repositories/`
4. **Service** → Write business logic in `app/services/`
5. **Route** → Create API endpoints in `app/api/v1/`
6. **Register** → Add your router to `app/api/v1/router.py`

After adding a new model, generate a migration:
```bash
alembic revision --autogenerate -m "add_your_table"
alembic upgrade head
```
