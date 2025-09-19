from typing import Optional, List
from pydantic import BaseModel, field_validator
from app.core.permissions import AppPermissions

# --- Role Schemas ---
class RoleBase(BaseModel):
    name: str
    description: str | None = None

class RoleCreate(RoleBase):
    permissions: List[str] = []

    @field_validator("permissions")
    def validate_permissions(cls, v):
        for permission in v:
            if permission not in [p.value for p in AppPermissions]:
                raise ValueError(f"Invalid permission: {permission}")
        return v

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None

    @field_validator("permissions")
    def validate_permissions(cls, v):
        if v is not None:
            for permission in v:
                if permission not in [p.value for p in AppPermissions]:
                    raise ValueError(f"Invalid permission: {permission}")
        return v

class RoleRead(RoleBase):
    id: int
    permissions: List[str] = []

    class Config:
        orm_mode = True