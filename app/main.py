from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.exception_handlers import setup_exception_handlers
from app.db.session import engine, AsyncSessionLocal
from app.db.initial_data import seed_initial_data
from app.api.routers import admin, profiles, rbac
from app.auth.auth import auth_backend, fastapi_users
from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.services.payment.router import router as payment_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    logger.info("Application startup...")
    setup_logging()
    async with AsyncSessionLocal() as db:
        await seed_initial_data(db)
    yield
    # On shutdown
    logger.info("Application shutdown...")
    await engine.dispose()

app = FastAPI(
    title="Scalable FastAPI Template",
    lifespan=lifespan,
    # ... other app config
)

setup_exception_handlers(app)

# Auth routes
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/api/v1/auth/jwt", tags=["Auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/v1/auth",
    tags=["Auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/api/v1/auth",
    tags=["Auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/api/v1/auth",
    tags=["Auth"],
)
# User management by admins (optional, if you want admins to manage users)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/api/v1/users",
    tags=["Users"],
)

# Custom routers
app.include_router(rbac.router, prefix="/api/v1/rbac", tags=["RBAC Management"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(profiles.router, prefix="/api/v1/profiles", tags=["Profiles"])
app.include_router(payment_router, prefix="/api/v1/payments", tags=["Payments"])