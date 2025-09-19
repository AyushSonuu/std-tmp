# app/api/exception_handlers.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger

from app.core.exceptions import CustomException

async def custom_exception_handler(request: Request, exc: CustomException):
    """Handles exceptions defined in app/core/exceptions.py"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Formats Pydantic's validation errors into a cleaner structure."""
    errors = []
    for error in exc.errors():
        errors.append({"field": ".".join(map(str, error["loc"])), "message": error["msg"]})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation Error", "errors": errors},
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handles any unexpected exceptions.
    Logs the full traceback and returns a generic 500 error.
    """
    logger.exception(f"An unhandled exception occurred for request: {request.method} {request.url}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred."},
    )

def setup_exception_handlers(app):
    app.add_exception_handler(CustomException, custom_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)