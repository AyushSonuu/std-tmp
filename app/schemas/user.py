from fastapi_users import schemas
from .rbac import RoleReadWithPermissions

class UserRead(schemas.BaseUser[int]):
    roles: list[RoleReadWithPermissions] = []

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass