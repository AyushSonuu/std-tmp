from typing import Optional
from pydantic import BaseModel

# --- Permission Schemas ---
class PermissionBase(BaseModel):
    name: str
    description: str | None = None

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class PermissionRead(PermissionBase):
    id: int

# --- Role Schemas ---
class RoleBase(BaseModel):
    name: str
    description: str | None = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class RoleRead(RoleBase):
    id: int

class RoleReadWithPermissions(RoleRead):
    permissions: list[PermissionRead] = []