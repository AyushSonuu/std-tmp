from fastapi_users import schemas
from .rbac import RoleRead

class UserRead(schemas.BaseUser[int]):
    roles: list[RoleRead] = []

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass