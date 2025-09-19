from fastapi import Depends, HTTPException, status, Request
from loguru import logger
from typing import Optional

from app.auth.auth import fastapi_users
from app.models.user import User
from app.core import permissions as perms

current_active_user = fastapi_users.current_user(active=True)

class RequiresPermission:
    def __init__(self, permission_name: str):
        self.permission_name = permission_name

    async def __call__(self, user: User = Depends(current_active_user)):
        user_permissions = {perm for role in user.roles for perm in role.permissions}

        if self.permission_name not in user_permissions:
            logger.warning(
                f"User '{user.email}' lacks required permission '{self.permission_name}'."
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {self.permission_name}",
            )
        return user

_method_to_action = {
    "GET": perms.ACTION_READ,
    "POST": perms.ACTION_CREATE,
    "PATCH": perms.ACTION_UPDATE,
    "PUT": perms.ACTION_UPDATE,
    "DELETE": perms.ACTION_DELETE,
}

def AutoPermission(override: Optional[str] = None):
    """
    A dependency that automatically determines and checks permissions.
    - If 'override' is provided, it uses that permission string.
    - Otherwise, it infers the permission from the request's URL and method.
      e.g., GET /api/v1/profiles/ -> requires "profiles:read"
    """

    async def dependency(request: Request, user: User = Depends(current_active_user)):
        required_permission = override

        if not required_permission:
            # Infer from request path and method
            path_parts = request.url.path.strip("/").split("/")
            # e.g., ['api', 'v1', 'profiles', '1']
            if len(path_parts) >= 3:
                resource = path_parts[2]
                action = _method_to_action.get(request.method)
                if resource and action:
                    required_permission = f"{resource}:{action}"

        if not required_permission:
            # If permission cannot be determined, deny access as a security precaution
            logger.warning(
                f"Could not determine permission for {request.method} {request.url.path}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission check failed",
            )

        # Check if user has the required permission
        user_permissions = {perm for role in user.roles for perm in role.permissions}
        if required_permission not in user_permissions:
            logger.warning(
                f"User '{user.email}' lacks required permission '{required_permission}' for {request.method} {request.url.path}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {required_permission}",
            )

        return user

    return dependency