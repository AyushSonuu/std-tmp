from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import AutoPermission
from app.core import permissions as perms
from app.auth.auth import fastapi_users, get_user_manager
from app.crud import crud_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate

router = APIRouter()

current_active_user = fastapi_users.current_user(active=True)


@router.get(
    "/me",
    response_model=UserRead,
)
async def read_users_me(current_user: User = Depends(current_active_user)):
    """
    Get current user.
    """
    return current_user


@router.patch("/me", response_model=UserRead)
async def update_user_me(
    user_update: UserUpdate,
    user_manager=Depends(get_user_manager),
    current_user: User = Depends(current_active_user),
):
    """
    Update own user.
    """
    updated_user = await user_manager.update(user_update, current_user)
    return updated_user


@router.get(
    "/",
    response_model=List[UserRead],
    dependencies=[Depends(AutoPermission(override=perms.AppPermissions.USERS_READ))],
)
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve users.
    """
    users = await crud_user.get_multi(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserRead)
async def read_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(AutoPermission(override=perms.AppPermissions.USERS_READ))
):
    """
    Get a specific user by id.
    A regular user can only see their own profile.
    An admin with 'users:read' can see any profile.
    """
    user_permissions = {perm for role in user.roles for perm in role.permissions}

    if user.id == user_id or perms.AppPermissions.USERS_READ in user_permissions:
        target_user = await crud_user.get(db, id=user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        return target_user
        
    raise HTTPException(status_code=403, detail="Not authorized to access this user's data")


@router.get(
    "/{user_id}/permissions",
    response_model=List[str],
    dependencies=[Depends(AutoPermission(override=perms.AppPermissions.USERS_READ))],
)
async def get_user_permissions(user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a flat list of all permission names for a specific user.
    """
    target_user = await crud_user.get(db, id=user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_permissions = {perm for role in target_user.roles for perm in role.permissions}
    return sorted(list(user_permissions))
