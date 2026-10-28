"""HTTP adapter, authentication and static React application."""
from pathlib import Path
from contextlib import asynccontextmanager
import os
import secrets
from typing import Annotated, Literal
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from backend import service
from backend.db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="ACME Salary Manager API", version="1.0.0", lifespan=lifespan)
security = HTTPBasic(auto_error=False)


def authenticate(credentials: Annotated[HTTPBasicCredentials | None, Depends(security)]) -> str:
    # No WWW-Authenticate challenge: the application renders its own sign-in form.
    # This prevents browsers from displaying a second, native credential dialog.
    if credentials is None:
        raise HTTPException(401, "Authentication required")
    username = os.getenv("ACME_ADMIN_USER")
    password = os.getenv("ACME_ADMIN_PASSWORD")
    if not username or not password:
        raise HTTPException(503, "Administrator credentials are not configured")
    if not (secrets.compare_digest(credentials.username.encode(), username.encode()) and
            secrets.compare_digest(credentials.password.encode(), password.encode())):
        raise HTTPException(401, "Invalid credentials")
    return username


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    # All JavaScript and CSS are bundled locally; no third-party runtime requests.
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
        "connect-src 'self'; img-src 'self' data:; "
        "object-src 'none'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    )
    response.headers["Cache-Control"] = "no-store" if request.url.path.startswith("/api/") else "no-cache"
    return response


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/me")
def me(actor: Annotated[str, Depends(authenticate)]):
    return {"username": actor, "role": "HR Manager"}


@app.get("/api/meta")
def meta(actor: Annotated[str, Depends(authenticate)]):
    return service.metadata()


@app.get("/api/employees")
def employees(
    actor: Annotated[str, Depends(authenticate)],
    q: str = "", country: str = "", department: str = "",
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 25,
    sort: Literal["employee_code", "full_name", "salary", "department", "country"] = "employee_code",
    direction: Literal["asc", "desc"] = "asc",
):
    return service.directory(q, country, department, page, page_size, sort, direction)


def handle_error(error):
    if isinstance(error, service.NotFound):
        raise HTTPException(404, str(error)) from error
    if isinstance(error, service.Conflict):
        raise HTTPException(409, str(error)) from error
    if isinstance(error, ValueError):
        raise HTTPException(422, str(error)) from error
    raise error


@app.get("/api/employees/{employee_id}")
def employee(employee_id: int, actor: Annotated[str, Depends(authenticate)]):
    try:
        return service.get_employee(employee_id)
    except service.NotFound as error:
        handle_error(error)


class SalaryUpdate(BaseModel):
    salary: str
    reason: str = Field(min_length=5, max_length=240)
    expected_version: int = Field(ge=0)


@app.patch("/api/employees/{employee_id}/salary")
def update_salary(employee_id: int, body: SalaryUpdate, actor: Annotated[str, Depends(authenticate)]):
    if not body.reason.strip():
        raise HTTPException(422, "A reason for the salary change is required")
    try:
        return service.edit_salary(employee_id, body.salary, body.reason, body.expected_version, actor)
    except (ValueError, service.NotFound, service.Conflict) as error:
        handle_error(error)


@app.get("/api/employees/{employee_id}/history")
def salary_history(employee_id: int, actor: Annotated[str, Depends(authenticate)]):
    try:
        return service.history(employee_id)
    except service.NotFound as error:
        handle_error(error)


@app.get("/api/analytics")
def pay_analytics(actor: Annotated[str, Depends(authenticate)], currency: str):
    if currency not in service.CURRENCY_CODES:
        raise HTTPException(422, "Choose a supported currency")
    return service.analytics(currency)


FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/assets", StaticFiles(directory=str(FRONTEND)), name="assets")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(FRONTEND / "index.html")
