# app/core/exceptions.py
from fastapi import status

class CustomException(Exception):
    """Base class for custom exceptions."""
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "An unexpected internal server error occurred."

    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail

class UserNotFoundException(CustomException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "User not found."

class InactiveUserException(CustomException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "User is inactive."

class NotAdminException(CustomException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "User does not have admin privileges."