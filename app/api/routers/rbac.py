from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import RequiresPermission
from app.core.permissions import AppPermissions
from app.db.session import get_db
from app.crud import crud_rbac, crud_user
from app.schemas import rbac as rbac_schemas
from app.models.rbac import Role

router = APIRouter()

# RBAC Management for Roles
# -------------------------

@router.post(
    "/roles",
    response_model=rbac_schemas.RoleRead,
    dependencies=[Depends(RequiresPermission(AppPermissions.RBAC_MANAGE))],
    status_code=status.HTTP_201_CREATED,
)
async def create_new_role(role_in: rbac_schemas.RoleCreate, db: AsyncSession = Depends(get_db)):
    """Create a new role."""
    existing_role = await crud_rbac.crud_role.get_by_name(db, name=role_in.name)
    if existing_role:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Role with this name already exists")
    return await crud_rbac.crud_role.create(db, obj_in=role_in)

@router.get(
    "/roles",
    response_model=List[rbac_schemas.RoleRead],
    dependencies=[Depends(RequiresPermission(AppPermissions.RBAC_MANAGE))],
)
async def get_all_roles(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get all roles."""
    return await crud_rbac.crud_role.get_multi(db, skip=skip, limit=limit)

@router.get(
    "/roles/{role_id}",
    response_model=rbac_schemas.RoleRead,
    dependencies=[Depends(RequiresPermission(AppPermissions.RBAC_MANAGE))],
)
async def get_role_by_id(role_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single role by its ID."""
    role = await crud_rbac.crud_role.get(db, id=role_id)
    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found")
    return role

@router.patch(
    "/roles/{role_id}",
    response_model=rbac_schemas.RoleRead,
    dependencies=[Depends(RequiresPermission(AppPermissions.RBAC_MANAGE))],
)
async def update_role_by_id(role_id: int, role_in: rbac_schemas.RoleUpdate, db: AsyncSession = Depends(get_db)):
    """Update a role's details, including its permissions."""
    role = await crud_rbac.crud_role.get(db, id=role_id)
    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found")
    # Check if new name is already taken
    if role_in.name and role_in.name != role.name:
        existing_role = await crud_rbac.crud_role.get_by_name(db, name=role_in.name)
        if existing_role:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Role name already in use")
    
    return await crud_rbac.crud_role.update(db, db_obj=role, obj_in=role_in)

@router.delete(
    "/roles/{role_id}",
    dependencies=[Depends(RequiresPermission(AppPermissions.RBAC_MANAGE))],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_role_by_id(role_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a role."""
    role = await crud_rbac.crud_role.get(db, id=role_id)
    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found")
    await crud_rbac.crud_role.remove(db, id=role_id)
    return

# RBAC Management for Assignments
# -------------------------------

@router.post(
    "/users/{user_id}/roles/{role_id}",
    response_model=rbac_schemas.RoleRead, # Consider a UserReadWithRoles schema
    dependencies=[Depends(RequiresPermission(AppPermissions.RBAC_MANAGE))],
)
async def assign_role_to_user(user_id: int, role_id: int, db: AsyncSession = Depends(get_db)):
    """Assign a role to a user."""
    user = await crud_user.crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    role = await crud_rbac.crud_role.get(db, id=role_id)
    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found")
    await crud_rbac.assign_role_to_user(db, user=user, role=role)
    return role

@router.delete(
    "/users/{user_id}/roles/{role_id}",
    dependencies=[Depends(RequiresPermission(AppPermissions.RBAC_MANAGE))],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_role_from_user(user_id: int, role_id: int, db: AsyncSession = Depends(get_db)):
    """Remove a role from a user."""
    user = await crud_user.crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    role = await crud_rbac.crud_role.get(db, id=role_id)
    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Role not found")
    
    await crud_rbac.remove_role_from_user(db, user=user, role=role)
    return